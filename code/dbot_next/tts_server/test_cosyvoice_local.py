"""
test_cosyvoice_local.py — Test local d'inférence CosyVoice 2 EU
==============================================================
- Télécharge les modèles CosyVoice (au premier lancement)
- Valide le clonage avec l'audio ~/cosyvoice_server/reference_voice.wav
- Écrit le résultat dans /tmp/test_cosy_m1.wav
"""

import os
import sys
import torchaudio
from cosyvoice2_eu import load

def main():
    print("⏳ Initialisation de CosyVoice 2 EU (Téléchargement des modèles au premier lancement)...")
    
    # Charger le modèle
    cosy = load()
    print("✅ Modèle chargé avec succès.")

    ref_wav = os.path.expanduser("~/cosyvoice_server/reference_voice.wav")
    out_wav = "/tmp/test_cosy_m1.wav"
    text = "Bonjour, je suis D-Bot, votre assistant personnel. Mon nouveau synthétiseur vocal fonctionne parfaitement sur votre Mac M1 Max Pro."

    if not os.path.exists(ref_wav):
        print(f"❌ Erreur : Fichier de référence vocale introuvable à {ref_wav}")
        sys.exit(1)

    print(f"🎙️  Lancement de la synthèse vocale en français...")
    print(f"📖 Texte à lire : '{text}'")
    
    try:
        # Synthèse vocale
        wav, sr = cosy.tts(text=text, prompt=ref_wav)
        
        # Enregistrement du fichier
        torchaudio.save(out_wav, wav, sr)
        print(f"💾 Fichier audio généré avec succès : {out_wav}")
        print("🎉 Inférence validée !")
    except Exception as e:
        print(f"❌ Erreur lors de la synthèse : {e}")

if __name__ == "__main__":
    main()
