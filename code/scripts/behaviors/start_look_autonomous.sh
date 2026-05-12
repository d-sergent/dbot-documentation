#!/bin/bash
# =================================================================
# D-Bot : Démo Look-At-Speaker en Mode AUTONOME (Headless)
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

# 2. Préparation Audio (Libération GDM + Headless)
sudo systemctl isolate multi-user.target
pulseaudio -k && pulseaudio --start --exit-idle-time=-1
sleep 2

# 3. Activation Ampli
amixer -c 0 cset numid=3 on
amixer -c 0 cset numid=4 on
amixer -c 0 cset numid=5 60
amixer -c 0 cset numid=6 60

# 4. Lancement de la démo (SANS affichage OpenCV pour éviter crash headless)
echo "🤖 Lancement démo Look-At-Speaker (Mode console)..."
python3 code/scripts/behaviors/look_at_speaker_v1.py --no-display
