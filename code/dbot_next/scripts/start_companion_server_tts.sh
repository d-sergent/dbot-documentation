#!/bin/zsh
# =============================================================================
# start_companion_server_tts.sh — Lancement du serveur TTS Mac (Port 8002)
# =============================================================================
# Usage :
#   ./Code/dbot_next/scripts/start_companion_server_tts.sh            # lancer
#   ./Code/dbot_next/scripts/start_companion_server_tts.sh --restart  # tuer + relancer
#   ./Code/dbot_next/scripts/start_companion_server_tts.sh --stop     # arrêter seulement
#   ./Code/dbot_next/scripts/start_companion_server_tts.sh --status   # état
#   ./Code/dbot_next/scripts/start_companion_server_tts.sh --logs     # suive logs
# =============================================================================

PYTHON="/Users/davidsergent/.venvs/mlx-audio/bin/python"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SERVER="$WORKSPACE/Code/dbot_next/companion_server_tts_mac.py"
LOG="/tmp/companion_server_tts.log"
PID_FILE="/tmp/companion_server_tts.pid"
PORT=8002

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'

echo "${BOLD}${BLUE}🤖 D-Bot TTS Companion Server (Port $PORT) — Manager${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

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
        echo "${YELLOW}⏹  Arrêt du serveur TTS existant (PID $pid)...${NC}"
        kill "$pid" 2>/dev/null || true
        sleep 2
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null || true
            echo "${RED}   → Forcé (SIGKILL)${NC}"
        else
            echo "${GREEN}   → Arrêté proprement.${NC}"
        fi
        rm -f "$PID_FILE"
    else
        echo "   (Aucun serveur TTS en cours)."
    fi
    local port_pid=$(lsof -ti:$PORT 2>/dev/null | head -1 || true)
    if [[ -n "$port_pid" ]]; then
        echo "${YELLOW}⚠  Port $PORT occupé (PID $port_pid), libération...${NC}"
        kill -9 "$port_pid" 2>/dev/null || true
    fi
}

start_server() {
    echo "${BLUE}▶  Démarrage du serveur TTS Mac sur le port $PORT...${NC}"
    echo "   Script  : $SERVER"
    echo "   Python  : $PYTHON"
    echo "   Log     : $LOG"
    echo "   Port    : $PORT"
    echo ""

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
    local pid=$(lsof -ti:$PORT 2>/dev/null || pgrep -f "companion_server_tts_mac" | tail -1 || true)
    if [[ -n "$pid" ]]; then
        echo "$pid" > "$PID_FILE"
    fi

    echo -n "   Attente du démarrage"
    for i in $(seq 1 45); do
        sleep 1
        echo -n "."
        if grep -q "Application startup complete" "$LOG" 2>/dev/null; then
            echo ""
            echo "${GREEN}✅ Serveur TTS opérationnel (PID $pid) sur le port $PORT${NC}"
            echo ""
            echo "   Pour suivre les logs en direct :"
            echo "   ${BOLD}tail -f $LOG${NC}"
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            return 0
        fi
        if ! kill -0 "$pid" 2>/dev/null; then
            echo ""
            echo "${RED}❌ Le serveur TTS a planté au démarrage ! Consultez les logs :${NC}"
            tail -20 "$LOG"
            exit 1
        fi
    done
    echo ""
    echo "${YELLOW}⚠  Timeout 45s — consultez : tail -f $LOG${NC}"
}

case "${1:-}" in
    --stop)
        stop_server
        echo "${GREEN}✅ Serveur TTS arrêté.${NC}"
        ;;
    --restart)
        stop_server
        echo ""
        : > "$LOG"
        start_server
        ;;
    --status)
        pid=$(find_server_pid)
        if [[ -n "$pid" ]]; then
            echo "${GREEN}✅ Serveur TTS en cours (PID $pid) sur le port $PORT${NC}"
            echo "   Dernières lignes du log :"
            tail -5 "$LOG"
        else
            echo "${RED}⏹  Serveur TTS arrêté.${NC}"
        fi
        ;;
    --logs)
        tail -f "$LOG"
        ;;
    "")
        pid=$(find_server_pid)
        if [[ -n "$pid" ]]; then
            echo "${YELLOW}⚠  Un serveur TTS est déjà en cours (PID $pid).${NC}"
            echo "   Utilisez --restart pour le relancer, ou --status pour vérifier."
            exit 0
        fi
        : > "$LOG"
        start_server
        ;;
    *)
        echo "Usage : $0 [--stop|--restart|--status|--logs]"
        exit 1
        ;;
esac
