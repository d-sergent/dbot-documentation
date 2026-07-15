"""
stt_streaming.py — Décodeur ASR en continu utilisant nvidia/nemotron-3.5-asr-streaming-0.6b.
========================================================================================
- Chargement du modèle de streaming NeMo sur GPU (CUDA)
- Gestion de l'état du décodeur (cache FastConformer) via BatchedFrameASRRNNT
- Analyse en temps réel pour détection rapide de mots-clés d'arrêt ("stop")
"""

import os
import sys
import torch
import numpy as np
from typing import Optional, Callable, List

import nemo.collections.asr as nemo_asr
from nemo.collections.asr.parts.utils.streaming_utils import BatchedFrameASRRNNT

class STTStreamingError(Exception):
    """Exception personnalisée pour le décodeur ASR streaming."""
    pass

class StreamingSTTNemotron:
    """
    Décodeur ASR en continu utilisant nvidia/nemotron-3.5-asr-streaming-0.6b.
    """
    def __init__(self, 
                 model_name: str = "nvidia/nemotron-3.5-asr-streaming-0.6b", 
                 device: str = "cpu", 
                 target_lang: str = "fr-FR", 
                 frame_len: float = 0.16, 
                 total_buffer: float = 4.0,
                 interrupt_callback: Optional[Callable[[], None]] = None):
        self.device = device
        self.target_lang = target_lang
        self.frame_len = frame_len
        self.total_buffer = total_buffer
        self.interrupt_callback = interrupt_callback
        
        self.stop_words = ["stop", "arrête", "arrêtez", "danger", "bloqué", "pause"]

        # Chargement du modèle avec repli automatique sur le CPU si CUDA échoue (OOM / fragmentation)
        try:
            print(f"⏳ [STT Streaming] Chargement de {model_name} sur {self.device.upper()}...")
            self.model = nemo_asr.models.ASRModel.from_pretrained(model_name=model_name, map_location=self.device)
            self.model = self.model.to(self.device)
            self.model.eval()
            print(f"✅ [STT Streaming] Modèle ASR chargé avec succès sur {self.device.upper()}.")
        except Exception as e:
            if "cuda" in self.device.lower() or "oom" in str(e).lower() or "memory" in str(e).lower() or "assert" in str(e).lower():
                print(f"⚠ [STT Streaming] Échec du chargement sur {self.device.upper()} ({e}).")
                print("⚠ [STT Streaming] Tentative de repli automatique sur le CPU (Cortex-A78)...")
                try:
                    self.device = "cpu"
                    # Nettoyage CUDA
                    torch.cuda.empty_cache()
                    
                    self.model = nemo_asr.models.ASRModel.from_pretrained(model_name=model_name, map_location="cpu")
                    self.model = self.model.to("cpu")
                    self.model.eval()
                    print("✅ [STT Streaming] Modèle ASR chargé avec succès sur CPU (Mode Secours).")
                except Exception as e_cpu:
                    raise STTStreamingError(f"Échec critique du chargement du modèle sur CPU : {e_cpu}")
            else:
                raise STTStreamingError(f"Échec du chargement du modèle NeMo : {e}")

        # Configuration du décodeur streaming de NeMo (cache-aware FastConformer)
        try:
            self.decoder = BatchedFrameASRRNNT(
                asr_model=self.model,
                frame_len=self.frame_len,
                total_buffer=self.total_buffer,
                batch_size=1
            )
            self.decoder.reset()
            print("✅ [STT Streaming] Décodeur streaming initialisé.")
        except Exception as e:
            raise STTStreamingError(f"Échec de l'initialisation de BatchedFrameASRRNNT : {e}")

        self.sample_rate = 16000
        self.chunk_samples = int(self.frame_len * self.sample_rate)

    def reset(self):
        """Réinitialise le décodeur et efface l'historique d'alignement."""
        self.decoder.reset()

    def process_chunk(self, chunk: np.ndarray) -> str:
        """
        Traite un chunk audio brut (numpy array mono 16kHz)
        et renvoie la transcription cumulative.
        
        Args:
            chunk (np.ndarray): Données PCM mono 16kHz (int16 ou float32).
            
        Returns:
            str: Texte transcrit jusqu'à présent dans le segment courant.
        """
        # Normalisation en float32 si nécessaire
        if chunk.dtype == np.int16:
            chunk = chunk.astype(np.float32) / 32768.0
            
        # Ajustement de la longueur au format attendu (chunk_samples)
        if len(chunk) < self.chunk_samples:
            chunk = np.pad(chunk, (0, self.chunk_samples - len(chunk)), mode='constant')
        elif len(chunk) > self.chunk_samples:
            chunk = chunk[:self.chunk_samples]

        try:
            # Transformation en tenseur PyTorch et envoi sur GPU/CPU
            audio_tensor = torch.tensor(chunk, dtype=torch.float32).unsqueeze(0).to(self.device)
            
            # Transcription via le décodeur NeMo
            hypotheses = self.decoder.transcribe(audio_tensor)
            
            if hypotheses and len(hypotheses) > 0:
                text = hypotheses[0]
                if not isinstance(text, str):
                    text = getattr(text, 'text', str(text))
                
                # Vérification rapide de mots-clés d'interruption
                if self.interrupt_callback and any(word in text.lower() for word in self.stop_words):
                    print(f"🚨 [STT Streaming] MOT-CLÉ D'ARRÊT DÉTECTÉ dans '{text}' ! Interruption...")
                    self.interrupt_callback()
                    
                return text
        except Exception as e:
            print(f"⚠ [STT Streaming] Erreur lors de l'inférence : {e}")
            
        return ""
