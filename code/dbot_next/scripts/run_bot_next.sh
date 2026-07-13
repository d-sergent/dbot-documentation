#!/bin/bash
# =================================================================
# D-Bot Next : Lancement de la boucle conversationnelle avancée
# =================================================================

# Détermination du dossier du script (chemin absolu)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# Recherche et export du fichier .env pour les clés API (remonte jusqu'au parent racine)
ENV_FILE=""
SEARCH_DIR="$SCRIPT_DIR"
for i in {1..5}; do
    if [ -f "$SEARCH_DIR/.env" ]; then
        ENV_FILE="$SEARCH_DIR/.env"
        break
    fi
    SEARCH_DIR=$(dirname "$SEARCH_DIR")
done

if [ -n "$ENV_FILE" ]; then
    echo "🔑 [D-Bot Next] Chargement des variables d'environnement depuis $ENV_FILE..."
    # On exporte les variables d'environnement proprement
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "⚠ [D-Bot Next] Attention : Fichier .env non trouvé. Inférence en mode local de secours."
fi

# Paramètres par défaut si non définis dans .env
export DBOT_STT_MODEL=${DBOT_STT_MODEL:-"nvidia/nemotron-3.5-asr-streaming-0.6b"}
export DBOT_LLM_MODEL=${DBOT_LLM_MODEL:-"qwen2.5:0.5b"}

# Chemin de recherche Python pour inclure la racine du dépôt
export PYTHONPATH="$SCRIPT_DIR/../..:$PYTHONPATH"

# Libération matérielle de la carte ALSA (Direct)
echo "🔊 [D-Bot Next] Arrêt de PulseAudio pour garantir l'accès exclusif ALSA..."
export XDG_RUNTIME_DIR=/run/user/$(id -u)
pulseaudio -k 2>/dev/null
sleep 2

# Lancement de l'orchestrateur de dialogue Next
echo "🚀 [D-Bot Next] Lancement de l'orchestrateur de conversation..."
python3 "$SCRIPT_DIR/../brain/async_conversation.py"
