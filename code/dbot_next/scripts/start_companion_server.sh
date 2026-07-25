#!/bin/zsh
# =============================================================================
# start_companion_server.sh — Lancement propre du serveur compagnon D-Bot Mac
# =============================================================================
# Usage :
#   ./Code/dbot_next/scripts/start_companion_server.sh            # lancer
#   ./Code/dbot_next/scripts/start_companion_server.sh --restart  # tuer + relancer
#   ./Code/dbot_next/scripts/start_companion_server.sh --stop     # arrêter seulement
#
# Le serveur écoute sur le port 8001 (WebSocket /conversation)
# Les logs sont disponibles dans /tmp/companion_server.log
# =============================================================================

PYTHON="/Users/davidsergent/.venvs/mlx-audio/bin/python"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SERVER="$WORKSPACE/Code/dbot_next/companion_server.py"
LOG="/tmp/companion_server.log"
PID_FILE="/tmp/companion_server.pid"

# ─── Couleurs ────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'

echo "${BOLD}${BLUE}🤖 D-Bot Companion Server — Gestionnaire de démarrage${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ─── Fonctions ───────────────────────────────────────────────────────────────
PORT=8001

find_server_pid() {
    if [[ -f "$PID_FILE" ]]; then
        local saved_pid=$(cat "$PID_FILE" 2>/dev/null)
        if [[ -n "$saved_pid" ]] && kill -0 "$saved_pid" 2>/dev/null; then
            echo "$saved_pid"
            return 0
        fi
    fi
    lsof -ti:$PORT 2>/dev/null | head -1 || true
}

stop_server() {
    local pid=$(find_server_pid)
    if [[ -n "$pid" ]]; then
        echo "${YELLOW}⏹  Arrêt du serveur existant (PID $pid)...${NC}"
        kill "$pid" 2>/dev/null || true
        sleep 2
        # Si toujours vivant → SIGKILL
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null || true
            echo "${RED}   → Forcé (SIGKILL)${NC}"
        else
            echo "${GREEN}   → Arrêté proprement.${NC}"
        fi
        rm -f "$PID_FILE"
    else
        echo "   (Aucun serveur en cours)."
    fi
    # Libérer le port 8001 si occupé
    local port_pid=$(lsof -ti:8001 2>/dev/null | head -1 || true)
    if [[ -n "$port_pid" ]]; then
        echo "${YELLOW}⚠  Port 8001 encore occupé (PID $port_pid), libération...${NC}"
        kill -9 "$port_pid" 2>/dev/null || true
    fi
}

start_server() {
    echo "${BLUE}▶  Démarrage du serveur...${NC}"
    echo "   Script  : $SERVER"
    echo "   Python  : $PYTHON"
    echo "   Log     : $LOG"
    echo "   Port    : 8001"
    echo ""

    # Vérifications préalables
    if [[ ! -f "$SERVER" ]]; then
        echo "${RED}❌ Fichier serveur introuvable : $SERVER${NC}"
        exit 1
    fi
    if [[ ! -x "$PYTHON" ]]; then
        echo "${RED}❌ Python introuvable : $PYTHON${NC}"
        exit 1
    fi
    export PYTHONUNBUFFERED=1
    ( "$PYTHON" -u "$SERVER" > "$LOG" 2>&1 < /dev/null & )

    echo -n "   Attente du démarrage"
    for i in $(seq 1 45); do
        sleep 1
        echo -n "."
        local pid=$(find_server_pid)
        if [[ -n "$pid" ]]; then
            echo "$pid" > "$PID_FILE"
        fi
        if grep -q "Application startup complete" "$LOG" 2>/dev/null; then
            echo ""
            echo "${GREEN}✅ Serveur compagnon opérationnel (PID ${pid:-inconnu}) sur le port 8001${NC}"
            echo ""
            if grep -q "Groq Whisper" "$LOG" 2>/dev/null; then
                echo "${GREEN}   🚀 Mode ASR : Groq Whisper Large v3 Turbo (Cloud, < 300 ms)${NC}"
            elif grep -q "Modèle ASR local" "$LOG" 2>/dev/null; then
                echo "${YELLOW}   ⚡ Mode ASR : Faster-Whisper small (Local CPU)${NC}"
            fi
            echo ""
            echo "   Pour suivre les logs en direct :"
            echo "   ${BOLD}tail -f $LOG${NC}"
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            return 0
        fi
    done

    echo ""
    echo "${YELLOW}⚠  Timeout 45s — le serveur est peut-être encore en cours de chargement.${NC}"
    echo "   Consultez : tail -f $LOG"
}

# ─── Traitement des arguments ─────────────────────────────────────────────────
case "${1:-}" in
    --stop)
        stop_server
        echo "${GREEN}✅ Serveur arrêté.${NC}"
        ;;
    --restart)
        stop_server
        echo ""
        : > "$LOG"  # Rotation du log
        start_server
        ;;
    --status)
        pid=$(find_server_pid)
        if [[ -n "$pid" ]]; then
            echo "${GREEN}✅ Serveur en cours (PID $pid)${NC}"
            echo "   Dernières lignes du log :"
            tail -5 "$LOG"
        else
            echo "${RED}⏹  Serveur arrêté.${NC}"
        fi
        ;;
    --logs)
        tail -f "$LOG"
        ;;
    "")
        # Lancement normal : vérifier si déjà en cours
        pid=$(find_server_pid)
        if [[ -n "$pid" ]]; then
            echo "${YELLOW}⚠  Un serveur est déjà en cours (PID $pid).${NC}"
            echo "   Utilisez --restart pour le relancer, ou --status pour vérifier."
            exit 0
        fi
        : > "$LOG"  # Rotation du log au démarrage propre
        start_server
        ;;
    *)
        echo "Usage : $0 [--stop|--restart|--status|--logs]"
        exit 1
        ;;
esac
