"""
test_edge_tts_voices.py — Évaluation et test des voix françaises Microsoft Edge TTS sur Mac.
"""

import sys
import os
import time
import asyncio
import subprocess
import edge_tts

VOICES = [
    ("fr-FR-HenriNeural", "Homme (Naturel & Calme)"),
    ("fr-FR-RemyMultilingualNeural", "Homme (Multilingue Expression)"),
    ("fr-FR-DeniseNeural", "Femme (Claire & Dynamique)"),
    ("fr-FR-EloiseNeural", "Femme (Douce)"),
]

TEXT = (
    "Bonjour ! Je suis D-Bot, votre robot compagnon bipède. "
    "La synthèse vocale Edge-TTS fonctionne en streaming direct, sans aucune limite ni fuite de mémoire."
)

OUTPUT_DIR = "/tmp/edge_tts_eval"
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def test_voice(voice_id, label):
    print(f"\n🗣️  [TEST VOIX] : {voice_id} ({label})")
    out_file = os.path.join(OUTPUT_DIR, f"{voice_id}.mp3")
    
    t0 = time.time()
    first_chunk_dt = None
    
    communicate = edge_tts.Communicate(TEXT, voice_id)
    
    with open(out_file, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                if first_chunk_dt is None:
                    first_chunk_dt = (time.time() - t0) * 1000
                f.write(chunk["data"])
                
    total_dt = (time.time() - t0) * 1000
    print(f"⏱️  [PROFILING] 1er chunk : {first_chunk_dt:.0f} ms | Fichier complet : {total_dt:.0f} ms")
    print(f"📁 Fichier généré : {out_file}")
    
    # Jouer l'audio sur les haut-parleurs du Mac via afplay
    print(f"🔊 Lecture audio sur les haut-parleurs Mac...")
    subprocess.run(["afplay", out_file])


async def main():
    print("🧠 === ÉVALUATION DES VOIX FR MICROSOFT EDGE-TTS === 🧠")
    print(f"📝 Texte de test : \"{TEXT}\"")
    
    for voice_id, label in VOICES:
        await test_voice(voice_id, label)
        await asyncio.sleep(0.5)

    print("\n✅ Évaluation terminée ! Tous les fichiers MP3 sont dans /tmp/edge_tts_eval")


if __name__ == "__main__":
    asyncio.run(main())
