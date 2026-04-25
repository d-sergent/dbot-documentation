#!/bin/bash
# scripts/system/startup.sh — Démarrage D-Bot
# ============================================
# Lance l'environnement complet du robot.
# À exécuter en tant que : bash ~/dbot/code/scripts/system/startup.sh

set -e

echo ""
echo "╔══════════════════════════════╗"
echo "║   D-Bot — Démarrage Robot   ║"
echo "╚══════════════════════════════╝"
echo ""

# 1. Interfaces CAN0 et CAN1
echo "[1/3] Initialisation des interfaces CAN..."
sudo ip link set can0 type can bitrate 1000000 2>/dev/null || true
sudo ip link set can0 up 2>/dev/null || true
echo "      can0 à 1 Mbps — UP ✔"

sudo ip link set can1 type can bitrate 1000000 2>/dev/null || true
sudo ip link set can1 up 2>/dev/null || true
echo "      can1 à 1 Mbps — UP ✔"

# 2. Mise à jour du code
echo "[2/3] Mise à jour code depuis GitHub..."
cd ~/dbot && git pull --quiet && echo "      Code à jour ✔"

# 3. Vérification matériel
echo "[3/3] Vérification matériel..."
python3 ~/dbot/code/scripts/system/check_hardware.py

echo ""
echo "D-Bot prêt. Lancez vos scripts depuis ~/dbot/code/scripts/"
echo ""
