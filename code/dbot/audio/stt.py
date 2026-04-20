from faster_whisper import WhisperModel
import time
import os

class LocalSTT:
    """
    Système de transcription vocale (Speech-to-Text) 100% hors-ligne.
    Utilise 'faster-whisper' en CUDA (GPU) pour une vitesse d'inférence en temps réel.
    """
    def __init__(self, model_size="small", device="cuda"):
        # Sur la Jetson Orin Nano, on utilise le GPU ("cuda") avec des calculs en float16 pour économiser la RAM
        print(f"⏳ [STT] Chargement du réseau neuronal auditif '{model_size}' sur le GPU...")
        start = time.time()
        
        try:
            self.model = WhisperModel(model_size, device=device, compute_type="float16")
            print(f"✅ [STT] Oreilles prêtes en {time.time() - start:.1f} secondes !")
        except Exception as e:
            print(f"❌ [STT] Erreur critique lors du chargement de Whisper: {e}")
            print("Êtes-vous sûr d'avoir installé les librairies CUDA nécessaires ?")

    def transcribe(self, audio_file_path: str) -> str:
        """
        Analyse un fichier audio et le transforme en texte.
        Retourne une chaîne de caractères vide si seul du silence ou du bruit est détecté.
        """
        if not os.path.exists(audio_file_path):
            print(f"❌ [STT] Fichier audio introuvable : {audio_file_path}")
            return ""

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
            print(f"❌ [STT] Échec de la retranscription : {e}")
            return ""

if __name__ == "__main__":
    # Test unitaire de chargement simple
    print("\n--- Test Auditif Local (Whisper) ---")
    stt = LocalSTT(model_size="small")
    print("Le chargement du modèle GPU est un succès.")
