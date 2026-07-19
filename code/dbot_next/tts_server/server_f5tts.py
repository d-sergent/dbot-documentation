"""
server_f5tts.py — Serveur TTS F5-TTS Français
==============================================
- A déployer sur le Mac M1 Max Pro.
- Expose une API HTTP POST /synthesize sur le réseau LAN local.
- Utilise la voix de référence configurée dans /Users/davidsergent/Downloads/LA-CAF-MIX-RADIO.mp3.
- Optimisé pour une faible latence (nfe_step=16).
"""

import os
import io
import tempfile
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from cached_path import cached_path
from f5_tts.api import F5TTS

app = FastAPI(title="D-Bot TTS Server (F5-TTS French)")

# Configuration des chemins sur le Mac
VOICE_REF_MP3 = "/Users/davidsergent/Downloads/LA-CAF-MIX-RADIO.mp3"
PORT = 7860

# Transcription exacte requise par F5-TTS pour la référence CAF
VOICE_REF_TEXT = (
    "Vous avez déclaré être sans ressources et vous toucher à ce titre plusieurs aides de votre CAF. "
    "C'est étrange car l'Ursafe nous dit que vous êtes cadres supérieurs. En CDI, curieux, non ?"
)

# Chargement du modèle au démarrage (une seule fois)
print("⏳ [TTS Server] Chargement de F5-TTS Français (RASPIAUDIO)...")
try:
    ckpt_file = str(cached_path("hf://RASPIAUDIO/F5-French-MixedSpeakers-reduced/model_last_reduced.pt"))
    vocab_file = str(cached_path("hf://RASPIAUDIO/F5-French-MixedSpeakers-reduced/vocab.txt"))
    
    f5_model = F5TTS(
        model="F5TTS_Base",
        ckpt_file=ckpt_file,
        vocab_file=vocab_file
    )
    print(f"✅ [TTS Server] Modèle F5-TTS initialisé sur : {f5_model.device}")
except Exception as e:
    print(f"❌ [TTS Server] Erreur lors du chargement de F5-TTS : {e}")
    f5_model = None

class SynthRequest(BaseModel):
    text: str

@app.get("/status")
def status():
    """Vérifie le statut du serveur et la présence de la voix de référence."""
    ref_exists = os.path.exists(VOICE_REF_MP3)
    return {
        "status": "ready" if f5_model is not None else "error",
        "device": getattr(f5_model, "device", "unknown"),
        "reference_voice_found": ref_exists,
        "reference_path": VOICE_REF_MP3
    }

@app.post("/synthesize")
async def synthesize(req: SynthRequest):
    """Synthétise du texte en WAV avec la voix de référence clonée (vitesse normale, nfe_step=16)."""
    if f5_model is None:
        raise HTTPException(status_code=500, detail="Modèle F5-TTS non initialisé.")
        
    if not os.path.exists(VOICE_REF_MP3):
        raise HTTPException(status_code=400, detail=f"Fichier de référence vocale introuvable à {VOICE_REF_MP3}")
        
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Le texte à synthétiser est vide.")
        
    try:
        print(f"🎙️  [TTS Server] Inférence pour : '{req.text}'")
        
        # F5-TTS écrit le fichier de sortie sur le disque.
        # On utilise un fichier temporaire pour éviter les conflits d'accès concurrents.
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name
            
        # Inférence avec nfe_step=16 (optimisé pour diviser la latence par 2)
        f5_model.infer(
            ref_file=VOICE_REF_MP3,
            ref_text=VOICE_REF_TEXT,
            gen_text=req.text,
            file_wave=tmp_path,
            nfe_step=16,
            speed=1.0  # Vitesse normale demandée
        )
        
        # Lire l'audio généré et le renvoyer sous forme de flux
        with open(tmp_path, "rb") as f:
            audio_content = f.read()
            
        # Nettoyage du fichier temporaire
        os.remove(tmp_path)
        
        return StreamingResponse(io.BytesIO(audio_content), media_type="audio/wav")
    except Exception as e:
        print(f"❌ [TTS Server] Erreur d'inférence : {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
