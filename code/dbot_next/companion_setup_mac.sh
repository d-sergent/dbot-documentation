#!/bin/bash
# companion_setup_mac.sh — Initialisation et installation de la stack IA sur le Mac Compagnon.

echo "⚙️  [Mac Setup] Vérification de l'environnement virtuel..."
VENV_PATH="$HOME/.venvs/mlx-audio"

if [ ! -d "$VENV_PATH" ]; then
    echo "📦 [Mac Setup] Création de l'environnement virtuel dans $VENV_PATH..."
    mkdir -p "$HOME/.venvs"
    # Utilisation de python3.11 (requis par les dépendances MLX / F5-TTS)
    if command -v python3.11 &>/dev/null; then
        python3.11 -m venv "$VENV_PATH"
    else
        echo "❌ Python 3.11 n'est pas installé sur ce Mac. Veuillez l'installer via Homebrew (brew install python@3.11)."
        exit 1
    fi
fi

echo "🔌 [Mac Setup] Activation du venv..."
source "$VENV_PATH/bin/activate"

echo "🔄 [Mac Setup] Mise à niveau de pip..."
pip install --upgrade pip

echo "📦 [Mac Setup] Installation/Mise à jour des dépendances ASR, LLM et TTS..."
# Installation de faster-whisper (pour la transcription rapide sur CPU)
# et des utilitaires serveur (fastapi, websockets, uvicorn)
pip install faster-whisper fastapi uvicorn websockets requests soundfile torch torchaudio

# Les bibliothèques MLX-Audio et F5-TTS doivent déjà être présentes si les serveurs TTS tournent.
# Dans le doute, on s'assure qu'elles sont opérationnelles.
if ! python3 -c "import mlx.core" &>/dev/null; then
    echo "📦 [Mac Setup] Installation de mlx..."
    pip install mlx
fi

echo "✅ [Mac Setup] Environnement virtuel prêt !"
echo "Pour démarrer le serveur compagnon :"
echo "  source $VENV_PATH/bin/activate"
echo "  python3 Code/dbot_next/companion_server.py"
