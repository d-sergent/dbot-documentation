"""
server_cosyvoice.py — Serveur TTS CosyVoice 2 EU
===============================================
- A déployer sur le Mac M1 Max Pro.
- Expose une API HTTP POST /synthesize sur le réseau LAN local.
- Utilise la voix de référence configurée dans ~/cosyvoice_server/reference_voice.wav.
"""

import os
import io
import numpy as np
import soundfile as sf
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from cosyvoice2_eu import load

app = FastAPI(title="D-Bot TTS Server (CosyVoice 2 EU)")

# Chemins absolus sur le Mac
VOICE_REF_WAV = os.path.expanduser("~/cosyvoice_server/reference_voice.wav")
PORT = 7860

# Chargement du modèle au démarrage (une seule fois)
print("⏳ [TTS Server] Chargement de CosyVoice 2 EU...")
try:
    cosy_model = load()
    print("✅ [TTS Server] Modèle CosyVoice 2 EU chargé avec succès.")
except Exception as e:
    print(f"❌ [TTS Server] Erreur lors du chargement de CosyVoice: {e}")
    cosy_model = None

class SynthRequest(BaseModel):
    text: str

@app.get("/status")
def status():
    """Vérifie le statut du serveur et la présence de la voix de référence."""
    ref_exists = os.path.exists(VOICE_REF_WAV)
    return {
        "status": "ready" if cosy_model is not None else "error",
        "reference_voice_found": ref_exists,
        "reference_path": VOICE_REF_WAV
    }

@app.post("/synthesize")
async def synthesize(req: SynthRequest):
    """Synthétise du texte en WAV avec la voix de référence clonée."""
    if cosy_model is None:
        raise HTTPException(status_code=500, detail="Modèle CosyVoice non initialisé.")
        
    if not os.path.exists(VOICE_REF_WAV):
        raise HTTPException(status_code=400, detail=f"Fichier de référence vocale introuvable à {VOICE_REF_WAV}")
        
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Le texte à synthétiser est vide.")
        
    try:
        print(f"🎙️  [TTS Server] Inférence pour : '{req.text}'")
        # Exécution de l'inférence zero-shot
        wav, sr = cosy_model.tts(text=req.text, prompt=VOICE_REF_WAV)
        
        # Conversion du tenseur PyTorch en tableau numpy
        audio_data = wav.squeeze(0).cpu().numpy()
        
        # Écriture dans un buffer mémoire au format WAV
        buf = io.BytesIO()
        sf.write(buf, audio_data, sr, format="WAV")
        buf.seek(0)
        
        return StreamingResponse(buf, media_type="audio/wav")
    except Exception as e:
        print(f"❌ [TTS Server] Erreur d'inférence : {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
