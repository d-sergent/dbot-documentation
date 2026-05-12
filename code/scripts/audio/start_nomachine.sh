#!/bin/bash
# =================================================================
# D-Bot : Démarrage en Mode DÉVELOPPEMENT (NoMachine)
# =================================================================

# Chargement des variables d'environnement depuis le .env
if [ -f "$(dirname "$0")/../../../.env" ]; then
    export $(grep -v '^#' "$(dirname "$0")/../../../.env" | xargs)
    echo "✅ Clés API chargées depuis le .env"
fi

echo "🖥️  [D-Bot] Passage en mode Graphique (graphical.target)..."
sudo systemctl isolate graphical.target
sleep 1

echo "🔊 [D-Bot] Activation de l'amplificateur matériel..."
amixer -c 0 cset numid=3 on
amixer -c 0 cset numid=4 on
amixer -c 0 cset numid=5 60
amixer -c 0 cset numid=6 60

echo "🤖 [D-Bot] Lancement du Chatbot v2 (Mode Développement)..."
python3 code/scripts/behaviors/chatbot_local_v2.py
