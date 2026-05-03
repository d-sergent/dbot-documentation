from faster_whisper import WhisperModel
import time
import os


class STTError(Exception):
    """Exception personnalisée pour les erreurs de transcription (STT)."""
    pass


class LocalSTT:
    """
    Système de transcription vocale (Speech-to-Text) 100% hors-ligne.
    Utilise 'faster-whisper' en CUDA (GPU) pour une vitesse d'inférence en temps réel.

    Args:
        model_size (str): Taille du modèle Whisper ("tiny", "base", "small", "medium", "large").
        device (str): Device pour l'inference ("cuda" ou "cpu").

    Returns:
        None: Initialise le modèle Whisper pour la transcription.
    """
    def __init__(self, model_size: str = "small", device: str = "cuda"):
        # Sur la Jetson Orin Nano, on utilise le GPU ("cuda") avec des calculs en float16 pour économiser la RAM
        print(f"⏳ [STT] Chargement du réseau neuronal auditif '{model_size}' sur le GPU...")
        start = time.time()
        
        try:
            self.model = WhisperModel(model_size, device=device, compute_type="float16")
            print(f"✅ [STT] Oreilles prêtes en {time.time() - start:.1f} secondes (Accélération GPU) !")
        except Exception as e:
            if "CUDA support" in str(e) or "CUDA" in str(e):
                print(f"⚠ [STT] Accélération GPU indisponible (CTranslate2 non compilé pour CUDA).")
                print(f"⚠ [STT] Passage sur le CPU (Cortex-A78)...")
                # Sur CPU, on utilise 'int8' pour un calcul très rapide sans perte de compréhension
                self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
                print(f"✅ [STT] Oreilles prêtes en {time.time() - start:.1f} secondes (Mode CPU) !")
            else:
                raise STTError(f"Erreur critique lors du chargement de Whisper: {e}")

    def transcribe(self, audio_file_path: str) -> str:
        """
        Analyse un fichier audio et le transforme en texte.
        Retourne une chaîne de caractères vide si seul du silence ou du bruit est détecté.

        Args:
            audio_file_path (str): Chemin vers le fichier audio à transcrire.

        Returns:
            str: Texte transcrit ou chaîne vide en cas d'erreur/silence.
        """
        if not os.path.exists(audio_file_path):
            raise STTError(f"Fichier audio introuvable : {audio_file_path}")

        start_time = time.time()
        try:
            # On force la langue en français pour que le modèle aille plus vite (il ne perd pas de temps à deviner la langue)
            segments, info = self.model.transcribe(audio_file_path, language="fr", beam_size=5)
            
            # Les segments s'affichent au fur et à mesure, on les joint pour avoir la phrase complète
            text = "".join([segment.text for segment in segments])
            clean_text = text.strip()
            
            elapsed = time.time() - start_time
            print(f"📝 [STT] Compris en {elapsed:.2f}s : \"{clean_text}\" (Probabilité: {info.language_probability*100:.1f}%)")
            
            return clean_text
        except Exception as e:
            raise STTError(f"Échec de la retranscription : {e}")


if __name__ == "__main__":
    # Test unitaire de chargement simple
    print("\n--- Test Auditif Local (Whisper) ---")
    stt = LocalSTT(model_size="small")
    print("Le chargement du modèle GPU est un succès.")