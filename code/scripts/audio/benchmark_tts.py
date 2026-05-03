"""
Script de benchmark pour le module TTS (Text-to-Speech).
Mesure la latence et la qualité de la synthèse vocale.
"""

import time
from dbot.audio.tts import LocalTTS

def benchmark_tts(text: str = "Bonjour, je suis un robot D-Bot.", voice_model_path=None):
    """
    Benchmark du module TTS pour évaluer ses performances.

    Args:
        text (str): Texte à synthétiser.
        voice_model_path (str, optional): Chemin vers le modèle vocal Piper.

    Returns:
        dict: Résultats du benchmark (latence, succès, chemin du fichier audio).
    """
    results = {
        "text": text,
        "latency_seconds": 0.0,
        "success": False,
        "audio_file": "",
        "error": None
    }

    try:
        # Initialisation du module TTS
        print(f"🔄 [Benchmark TTS] Initialisation du module TTS...")
        tts = LocalTTS(voice_model_path=voice_model_path)

        # Génération de l'audio
        print(f"🔄 [Benchmark TTS] Génération de l'audio pour : '{text}'...")
        start_time = time.time()
        
        # Génération du fichier audio
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            temp_wav = tf.name

        gen_cmd = f'echo "{text}" | piper -m {tts.voice_model_path} --output_file {temp_wav}'
        import subprocess
        result = subprocess.run(gen_cmd, shell=True, stderr=subprocess.DEVNULL)
        
        if result.returncode != 0:
            raise Exception("Piper a échoué à générer le fichier audio.")

        results["latency_seconds"] = time.time() - start_time
        results["audio_file"] = temp_wav
        results["success"] = True
        
        print(f"✅ [Benchmark TTS] Succès ! Fichier audio généré : {temp_wav}")
    except Exception as e:
        print(f"❌ [Benchmark TTS] Erreur : {e}")
        results["error"] = str(e)
        results["success"] = False

    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        results = benchmark_tts(text=sys.argv[1])
    else:
        results = benchmark_tts()

    print("\n--- Résultats du Benchmark TTS ---")
    print(f"✅ Succès : {results['success']}")
    if results["error"]:
        print(f"⚠️ Erreur : {results['error']}")
    print(f"⏱️  Latence : {results['latency_seconds']:.2f} secondes")
    if results["success"]:
        print(f"🎵 Fichier audio généré : {results['audio_file']}")
    print(f"📝 Texte synthétisé : {results['text']}")