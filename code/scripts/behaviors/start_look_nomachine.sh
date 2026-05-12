#!/bin/bash
# =================================================================
# D-Bot : Démo Look-At-Speaker en Mode DÉVELOPPEMENT (NoMachine)
# =================================================================

# 1. Recherche et export du .env
ENV_FILE=""
SEARCH_DIR=$(dirname "$0")
for i in {1..4}; do
    if [ -f "$SEARCH_DIR/.env" ]; then
        ENV_FILE="$SEARCH_DIR/.env"
        break
    fi
    SEARCH_DIR=$(dirname "$SEARCH_DIR")
done
if [ -n "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
    echo "✅ Environnement chargé."
fi

# 2. Activation Ampli
amixer -c 0 cset numid=3 on
amixer -c 0 cset numid=4 on
amixer -c 0 cset numid=5 60
amixer -c 0 cset numid=6 60

# 3. Lancement de la démo (AVEC affichage vidéo)
echo "🖥️  Lancement démo Look-At-Speaker (Mode visuel)..."
python3 code/scripts/behaviors/look_at_speaker_v1.py
