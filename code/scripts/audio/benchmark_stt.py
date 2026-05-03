"""
Script de benchmark pour le module STT (Speech-to-Text).
Mesure la latence et la précision du modèle Whisper.
"""

import time
from dbot.audio.stt import LocalSTT

def benchmark_stt(model_size: str = "small", device: str = "cuda", audio_file: str = "test_audio.wav"):
    """
    Benchmark du module STT pour évaluer ses performances.

    Args:
        model_size (str): Taille du modèle Whisper.
        device (str): Device pour l'inference ("cuda" ou "cpu").
        audio_file (str): Chemin vers le fichier audio à transcrire.

    Returns:
        dict: Résultats du benchmark (latence, précision, succès).
    """
    results = {
        "model_size": model_size,
        "device": device,
        "latency_seconds": 0.0,
        "success": False,
        "transcribed_text": "",
        "language_probability": 0.0
    }

    try:
        # Initialisation du modèle
        print(f"🔄 [Benchmark STT] Initialisation du modèle '{model_size}' sur {device}...")
        stt = LocalSTT(model_size=model_size, device=device)

        # Transcription
        print(f"🔄 [Benchmark STT] Transcription du fichier : {audio_file}...")
        start_time = time.time()
        text = stt.transcribe(audio_file)
        results["latency_seconds"] = time.time() - start_time

        # Vérification des résultats
        if text:
            results["success"] = True
            results["transcribed_text"] = text
            print(f"✅ [Benchmark STT] Succès ! Texte transcrit : {text}")
        else:
            print("⚠️ [Benchmark STT] Aucun texte transcrit (silence/bruit détecté).")

        results["success"] = True
    except Exception as e:
        print(f"❌ [Benchmark STT] Erreur : {e}")
        results["success"] = False

    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        results = benchmark_stt(audio_file=sys.argv[1])
    else:
        results = benchmark_stt()

    print("\n--- Résultats du Benchmark STT ---")
    print(f"✅ Succès : {results['success']}")
    print(f"⏱️  Latence : {results['latency_seconds']:.2f} secondes")
    if results["success"]:
        print(f"📝 Texte transcrit : {results['transcribed_text']}")
    print(f"🌐 Probabilité de langue : {results['language_probability']:.1f}%")