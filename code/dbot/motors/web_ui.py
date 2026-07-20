#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dbot/motors/web_ui.py — Interface Web UI de Diagnostic et Contrôle du Cou D-Bot
==============================================================================
Serveur Web léger (HTTP + API JSON) pour la télémétrie et l'asservissement
en temps réel des moteurs RS-05 du cou (Pan ID:1, Tilt ID:2).

Utilisation sur la Jetson :
    python3 -m dbot.motors.web_ui
    # ou
    python3 Code/dbot/motors/web_ui.py --port 8080

Accès depuis le Mac (sur le même réseau Wi-Fi) :
    http://ubuntu.local:8080  ou  http://<IP_JETSON>:8080
"""

import sys
import os
import json
import math
import time
import argparse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# S'assurer que le paquet 'dbot' est accessible
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from dbot.motors.neck import NeckController
    from dbot.config import (
        PAN_MIN_RAD, PAN_MAX_RAD,
        TILT_MIN_RAD, TILT_MAX_RAD,
        CAN_CHANNEL, CAN_BITRATE
    )
    HAS_DBOT_HARDWARE = True
except Exception as e:
    print(f"⚠️ Avertissement : Impossible d'importer l'équipement D-Bot ({e}). Mode simulation activé.")
    HAS_DBOT_HARDWARE = False
    PAN_MIN_RAD, PAN_MAX_RAD = math.radians(-80), math.radians(80)
    TILT_MIN_RAD, TILT_MAX_RAD = math.radians(-20), math.radians(30)
    CAN_CHANNEL, CAN_BITRATE = 'can0', 1000000


# ── Modèle d'Équipement / Telemetry Manager ─────────────────

class MotorState:
    def __init__(self):
        self.lock = threading.Lock()
        self.enabled = False
        self.simulated = not HAS_DBOT_HARDWARE
        
        self.pan_target_deg = 0.0
        self.tilt_target_deg = 0.0
        
        self.pan_deg = 0.0
        self.tilt_deg = 0.0
        self.pan_vel_dps = 0.0
        self.tilt_vel_dps = 0.0
        self.vbus_v = 0.0
        
        self.pan_online = False
        self.tilt_online = False
        self.neck_controller = None
        
        if HAS_DBOT_HARDWARE:
            try:
                self.neck_controller = NeckController()
            except Exception as err:
                print(f"❌ Erreur d'initialisation NeckController: {err}")

    def update_telemetry(self):
        """Met à jour l'état télémétrique depuis le bus CAN ou la simulation."""
        with self.lock:
            if self.neck_controller and HAS_DBOT_HARDWARE:
                try:
                    detected = self.neck_controller.detect()
                    self.pan_online = detected.get(1, False)
                    self.tilt_online = detected.get(2, False)
                    
                    # Toujours lire la position réelle et le Vbus, même si les moteurs sont désactivés !
                    state = self.neck_controller.get_state()
                    self.pan_deg = state.get('pan_deg', 0.0)
                    self.tilt_deg = state.get('tilt_deg', 0.0)
                    self.pan_vel_dps = state.get('pan_vel_dps', 0.0)
                    self.tilt_vel_dps = state.get('tilt_vel_dps', 0.0)
                    self.vbus_v = state.get('vbus_v', 0.0)
                except Exception as ex:
                    print(f"⚠️ Erreur de télémétrie CAN: {ex}")
            else:
                # Mode simulation pour test sans robot physique
                self.pan_online = True
                self.tilt_online = True
                self.vbus_v = 48.1
                if self.enabled:
                    # Simulation d'interpolation fluide
                    self.pan_deg += (self.pan_target_deg - self.pan_deg) * 0.2
                    self.tilt_deg += (self.tilt_target_deg - self.tilt_deg) * 0.2
                    self.pan_vel_dps = (self.pan_target_deg - self.pan_deg) * 2.0
                    self.tilt_vel_dps = (self.tilt_target_deg - self.tilt_deg) * 2.0

    def enable(self):
        with self.lock:
            if self.neck_controller and HAS_DBOT_HARDWARE:
                try:
                    self.neck_controller.emergency_stopped = False
                    self.neck_controller.detect()
                    self.neck_controller.enable()
                except Exception as e:
                    print(f"❌ Échec d'activation moteur: {e}")
            
            # 🎯 ACCROCHAGE SÉCURISÉ : La consigne prend la position physique réelle au lieu de 0.0° !
            norm_pan = self._normalize_angle(self.pan_deg)
            norm_tilt = self._normalize_angle(self.tilt_deg)
            self.pan_target_deg = norm_pan
            self.tilt_target_deg = norm_tilt

            self.enabled = True
            return {"status": "success", "enabled": True}

    def disable(self):
        # 🚨 E-STOP PRIORITAIRE : Ne doit PAS attendre self.lock
        if self.neck_controller and HAS_DBOT_HARDWARE:
            try:
                self.neck_controller.emergency_stopped = True
                self.neck_controller.disable()
            except Exception as e:
                print(f"❌ Échec de désactivation E-STOP: {e}")
        with self.lock:
            self.enabled = False
        return {"status": "success", "enabled": False}

    def set_look_at(self, pan_deg: float, tilt_deg: float):
        with self.lock:
            # Clamp aux limites
            pan_deg = max(math.degrees(PAN_MIN_RAD), min(math.degrees(PAN_MAX_RAD), pan_deg))
            tilt_deg = max(math.degrees(TILT_MIN_RAD), min(math.degrees(TILT_MAX_RAD), tilt_deg))
            
            self.pan_target_deg = pan_deg
            self.tilt_target_deg = tilt_deg
            
            if self.enabled and self.neck_controller and HAS_DBOT_HARDWARE:
                if getattr(self.neck_controller, 'emergency_stopped', False):
                    print("🚨 Mouvement refusé : E-STOP actif.")
                    return {"status": "error", "message": "E-STOP active"}
                
                # Exécution dans un thread séparé pour NE PAS bloquer le serveur ni E-STOP
                def run_movement():
                    try:
                        self.neck_controller.look_at(pan_deg, tilt_deg)
                    except Exception as e:
                        print(f"⚠️ Erreur de commande look_at: {e}")
                
                t = threading.Thread(target=run_movement, daemon=True)
                t.start()
                    
            return {
                "status": "success",
                "pan_target": self.pan_target_deg,
                "tilt_target": self.tilt_target_deg
            }

    def _normalize_angle(self, deg: float) -> float:
        """Normalise un angle 0-360° dans la plage [-180°, +180°]."""
        deg = deg % 360.0
        if deg > 180.0:
            deg -= 360.0
        return deg

    def get_json_state(self):
        with self.lock:
            norm_pan = self._normalize_angle(self.pan_deg)
            norm_tilt = self._normalize_angle(self.tilt_deg)
            return {
                "enabled": self.enabled,
                "simulated": self.simulated,
                "can_channel": CAN_CHANNEL,
                "can_bitrate": CAN_BITRATE,
                "pan_online": self.pan_online,
                "tilt_online": self.tilt_online,
                "pan_deg": round(norm_pan, 2),
                "tilt_deg": round(norm_tilt, 2),
                "pan_target_deg": round(self.pan_target_deg, 2),
                "tilt_target_deg": round(self.tilt_target_deg, 2),
                "pan_vel_dps": round(self.pan_vel_dps, 2),
                "tilt_vel_dps": round(self.tilt_vel_dps, 2),
                "vbus_v": round(self.vbus_v, 1),
                "limits": {
                    "pan_min": round(math.degrees(PAN_MIN_RAD), 1),
                    "pan_max": round(math.degrees(PAN_MAX_RAD), 1),
                    "tilt_min": round(math.degrees(TILT_MIN_RAD), 1),
                    "tilt_max": round(math.degrees(TILT_MAX_RAD), 1),
                }
            }


GLOBAL_STATE = MotorState()

# ── Serveur HTTP & Handlers ─────────────────────────────────

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Serveur HTTP multithreadé non-bloquant."""
    daemon_threads = True


class WebUIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Désactiver les logs verbeux de chaque requête GET /api/state
        pass

    def send_json(self, data, code=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html_str):
        body = html_str.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/api/state':
            self.send_json(GLOBAL_STATE.get_json_state())
        elif self.path == '/' or self.path == '/index.html':
            self.send_html(HTML_TEMPLATE)
        else:
            self.send_error(404, "Page non trouvée")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = {}
        if content_length > 0:
            try:
                post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
            except Exception:
                pass

        if self.path == '/api/enable':
            res = GLOBAL_STATE.enable()
            self.send_json(res)
        elif self.path == '/api/disable':
            res = GLOBAL_STATE.disable()
            self.send_json(res)
        elif self.path == '/api/look_at':
            pan = float(post_data.get('pan_deg', 0.0))
            tilt = float(post_data.get('tilt_deg', 0.0))
            res = GLOBAL_STATE.set_look_at(pan, tilt)
            self.send_json(res)
        elif self.path == '/api/center':
            res = GLOBAL_STATE.set_look_at(0.0, 0.0)
            self.send_json(res)
        elif self.path == '/api/estop':
            GLOBAL_STATE.set_look_at(0.0, 0.0)
            res = GLOBAL_STATE.disable()
            self.send_json({"status": "ESTOP_TRIGGERED", "enabled": False})
        else:
            self.send_error(404, "Endpoint API non trouvé")


# ── Dashboard HTML / CSS / JavaScript ───────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D-Bot — Motorbridge Web UI (Tête & Cou)</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --border-color: rgba(255, 255, 255, 0.1);
            --accent-blue: #38bdf8;
            --accent-green: #22c55e;
            --accent-red: #ef4444;
            --accent-orange: #f97316;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            padding: 24px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .header {
            width: 100%;
            max-width: 900px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-color);
        }

        .title-area h1 {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--accent-blue);
        }

        .title-area p {
            font-size: 0.85rem;
            color: var(--text-muted);
        }

        .badge-status {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 20px;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            font-size: 0.85rem;
        }

        .dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--accent-red);
        }

        .dot.online { background: var(--accent-green); box-shadow: 0 0 8px var(--accent-green); }

        .grid-container {
            width: 100%;
            max-width: 900px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }

        .card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .card-header {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 16px;
            color: var(--accent-blue);
            display: flex;
            justify-content: space-between;
        }

        .stat-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 16px;
        }

        .stat-box {
            background: rgba(15, 23, 42, 0.6);
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            text-align: center;
        }

        .stat-label {
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
        }

        .stat-value {
            font-size: 1.4rem;
            font-weight: 700;
            margin-top: 4px;
        }

        .control-group {
            margin-top: 16px;
        }

        .control-label {
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            margin-bottom: 8px;
        }

        .slider-limits {
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 4px;
        }

        input[type=range] {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #334155;
            outline: none;
            accent-color: var(--accent-blue);
        }

        .btn-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 16px;
        }

        .btn {
            padding: 12px 16px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-primary { background: var(--accent-blue); color: #0f172a; }
        .btn-primary:hover { background: #7dd3fc; }

        .btn-secondary { background: #334155; color: var(--text-main); }
        .btn-secondary:hover { background: #475569; }

        .btn-danger { background: var(--accent-red); color: #ffffff; grid-column: span 2; }
        .btn-danger:hover { background: #dc2626; box-shadow: 0 0 16px rgba(239, 68, 68, 0.5); }

        .btn-success { background: var(--accent-green); color: #0f172a; }
        .btn-success:hover { background: #4ade80; }

        .visualizer {
            width: 100%;
            height: 180px;
            background: rgba(15, 23, 42, 0.8);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            position: relative;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .target-crosshair {
            width: 24px;
            height: 24px;
            border: 2px solid var(--accent-orange);
            border-radius: 50%;
            position: absolute;
            transform: translate(-50%, -50%);
            transition: all 0.1s linear;
        }

        .current-head {
            width: 16px;
            height: 16px;
            background: var(--accent-blue);
            border-radius: 50%;
            position: absolute;
            transform: translate(-50%, -50%);
            box-shadow: 0 0 12px var(--accent-blue);
            transition: all 0.05s linear;
        }
    </style>
</head>
<body>

    <div class="header">
        <div class="title-area">
            <h1>🤖 D-Bot Motorbridge Web UI</h1>
            <p>Télémétrie et Asservissement Moteurs Cou RS-05 (Bus CAN: <span id="can-info">can0 @ 1Mbps</span>)</p>
        </div>
        <div class="badge-status">
            <div id="status-dot" class="dot"></div>
            <span id="status-text">Hors ligne</span>
        </div>
    </div>

    <div class="grid-container">

        <!-- Carte 1 : Télémétrie Moteur Pan (ID 1) -->
        <div class="card">
            <div class="card-header">
                <span>Pan (Rotation Gauche/Droite)</span>
                <span style="font-size:0.85rem; color:var(--text-muted)">ID: 1</span>
            </div>
            <div class="stat-group">
                <div class="stat-box">
                    <div class="stat-label">Position Angle</div>
                    <div id="pan-deg" class="stat-value">0.0°</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Vitesse</div>
                    <div id="pan-vel" class="stat-value">0.0°/s</div>
                </div>
            </div>
            <div class="control-group">
                <div class="control-label">
                    <span>Consigne Pan</span>
                    <span id="pan-target-val">0.0°</span>
                </div>
                <input type="range" id="pan-slider" min="-80" max="80" value="0" step="0.5">
                <div class="slider-limits">
                    <span id="pan-min-label">Min: -80.0°</span>
                    <span id="pan-max-label">Max: +80.0°</span>
                </div>
            </div>
        </div>

        <!-- Carte 2 : Télémétrie Moteur Tilt (ID 2) -->
        <div class="card">
            <div class="card-header">
                <span>Tilt (Inclinaison Avant/Arrière)</span>
                <span style="font-size:0.85rem; color:var(--text-muted)">ID: 2</span>
            </div>
            <div class="stat-group">
                <div class="stat-box">
                    <div class="stat-label">Position Angle</div>
                    <div id="tilt-deg" class="stat-value">0.0°</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Vitesse</div>
                    <div id="tilt-vel" class="stat-value">0.0°/s</div>
                </div>
            </div>
            <div class="control-group">
                <div class="control-label">
                    <span>Consigne Tilt</span>
                    <span id="tilt-target-val">0.0°</span>
                </div>
                <input type="range" id="tilt-slider" min="-20" max="30" value="0" step="0.5">
                <div class="slider-limits">
                    <span id="tilt-min-label">Min: -20.0°</span>
                    <span id="tilt-max-label">Max: +30.0°</span>
                </div>
            </div>
        </div>

        <!-- Carte 3 : Représentation 2D du Regard -->
        <div class="card">
            <div class="card-header">
                <span>Visualiseur 2D du Regard</span>
                <span id="vbus-val" style="color:var(--accent-green)">48.0V</span>
            </div>
            <div class="visualizer" id="visualizer">
                <div id="crosshair" class="target-crosshair"></div>
                <div id="head-dot" class="current-head"></div>
            </div>
        </div>

        <!-- Carte 4 : Commandes Système & Sécurité -->
        <div class="card">
            <div class="card-header">
                <span>Contrôle & Sécurité Moteurs</span>
            </div>
            <div class="btn-grid">
                <button id="btn-enable" class="btn btn-success">Activer Moteurs</button>
                <button id="btn-disable" class="btn btn-secondary">Désactiver</button>
                <button id="btn-center" class="btn btn-primary" style="grid-column: span 2">Recentrer Tête (0°, 0°)</button>
                <button id="btn-estop" class="btn btn-danger">🚨 ARRÊT D'URGENCE (E-STOP)</button>
            </div>
        </div>

    </div>

    <script>
        const panSlider = document.getElementById('pan-slider');
        const tiltSlider = document.getElementById('tilt-slider');
        const panTargetVal = document.getElementById('pan-target-val');
        const tiltTargetVal = document.getElementById('tilt-target-val');

        const panDeg = document.getElementById('pan-deg');
        const tiltDeg = document.getElementById('tilt-deg');
        const panVel = document.getElementById('pan-vel');
        const tiltVel = document.getElementById('tilt-vel');
        const vbusVal = document.getElementById('vbus-val');

        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        const canInfo = document.getElementById('can-info');

        const crosshair = document.getElementById('crosshair');
        const headDot = document.getElementById('head-dot');

        let isUserDragging = false;

        function updateVisualizer(targetPan, targetTilt, currentPan, currentTilt) {
            // Conversion [-80, 80] Pan -> [10%, 90%] X
            // Conversion [-20, 30] Tilt -> [10%, 90%] Y
            const targetX = 50 + (targetPan / 80) * 40;
            const targetY = 50 + (targetTilt / 30) * 40;

            const currentX = 50 + (currentPan / 80) * 40;
            const currentY = 50 + (currentTilt / 30) * 40;

            crosshair.style.left = targetX + '%';
            crosshair.style.top = targetY + '%';

            headDot.style.left = currentX + '%';
            headDot.style.top = currentY + '%';
        }

        async function fetchState() {
            try {
                const res = await fetch('/api/state');
                const data = await res.json();

                canInfo.innerText = data.can_channel + ' @ ' + (data.can_bitrate / 1000000) + 'Mbps';
                
                if (data.enabled) {
                    statusDot.classList.add('online');
                    statusText.innerText = data.simulated ? 'Mode Simulé' : 'Moteurs En Ligne';
                } else {
                    statusDot.classList.remove('online');
                    statusText.innerText = 'Moteurs Désactivés';
                }

                panDeg.innerText = data.pan_deg.toFixed(1) + '°';
                tiltDeg.innerText = data.tilt_deg.toFixed(1) + '°';
                panVel.innerText = data.pan_vel_dps.toFixed(1) + '°/s';
                tiltVel.innerText = data.tilt_vel_dps.toFixed(1) + '°/s';
                vbusVal.innerText = data.vbus_v.toFixed(1) + 'V';

                if (data.limits) {
                    panSlider.min = data.limits.pan_min;
                    panSlider.max = data.limits.pan_max;
                    tiltSlider.min = data.limits.tilt_min;
                    tiltSlider.max = data.limits.tilt_max;
                    document.getElementById('pan-min-label').innerText = 'Min: ' + data.limits.pan_min.toFixed(1) + '°';
                    document.getElementById('pan-max-label').innerText = 'Max: +' + data.limits.pan_max.toFixed(1) + '°';
                    document.getElementById('tilt-min-label').innerText = 'Min: ' + data.limits.tilt_min.toFixed(1) + '°';
                    document.getElementById('tilt-max-label').innerText = 'Max: +' + data.limits.tilt_max.toFixed(1) + '°';
                }

                if (!isUserDragging) {
                    panSlider.value = data.pan_target_deg;
                    tiltSlider.value = data.tilt_target_deg;
                    panTargetVal.innerText = data.pan_target_deg.toFixed(1) + '°';
                    tiltTargetVal.innerText = data.tilt_target_deg.toFixed(1) + '°';
                }

                updateVisualizer(data.pan_target_deg, data.tilt_target_deg, data.pan_deg, data.tilt_deg);

            } catch (err) {
                statusDot.classList.remove('online');
                statusText.innerText = 'Déconnecté du Serveur';
            }
        }

        function sendLookAt(pan, tilt) {
            fetch('/api/look_at', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({pan_deg: parseFloat(pan), tilt_deg: parseFloat(tilt)})
            });
        }

        panSlider.addEventListener('mousedown', () => isUserDragging = true);
        tiltSlider.addEventListener('mousedown', () => isUserDragging = true);

        panSlider.addEventListener('mouseup', () => {
            isUserDragging = false;
            sendLookAt(panSlider.value, tiltSlider.value);
        });
        tiltSlider.addEventListener('mouseup', () => {
            isUserDragging = false;
            sendLookAt(panSlider.value, tiltSlider.value);
        });

        panSlider.addEventListener('input', () => {
            panTargetVal.innerText = parseFloat(panSlider.value).toFixed(1) + '°';
        });
        tiltSlider.addEventListener('input', () => {
            tiltTargetVal.innerText = parseFloat(tiltSlider.value).toFixed(1) + '°';
        });

        document.getElementById('btn-enable').onclick = () => fetch('/api/enable', {method: 'POST'});
        document.getElementById('btn-disable').onclick = () => fetch('/api/disable', {method: 'POST'});
        document.getElementById('btn-center').onclick = () => {
            panSlider.value = 0;
            tiltSlider.value = 0;
            panTargetVal.innerText = '0.0°';
            tiltTargetVal.innerText = '0.0°';
            fetch('/api/center', {method: 'POST'});
        };
        document.getElementById('btn-estop').onclick = () => fetch('/api/estop', {method: 'POST'});

        setInterval(fetchState, 100);
    </script>
</body>
</html>
"""


# ── Thread de Télémétrie Arrière-Plan ──────────────────────

def telemetry_loop():
    while True:
        GLOBAL_STATE.update_telemetry()
        time.sleep(0.05)  # 20 Hz


def main():
    parser = argparse.ArgumentParser(description="Serveur Web UI Motorbridge D-Bot pour le Cou RS-05")
    parser.add_argument("--host", default="0.0.0.0", help="Adresse d'écoute (0.0.0.0 = toutes les interfaces)")
    parser.add_argument("--port", type=int, default=8080, help="Port Web (défaut: 8080)")
    args = parser.parse_args()

    # Démarrage du thread de mise à jour télémétrique
    t = threading.Thread(target=telemetry_loop, daemon=True)
    t.start()

    server_address = (args.host, args.port)
    httpd = ThreadedHTTPServer(server_address, WebUIHandler)
    print(f"\n========================================================")
    print(f"🚀 Serveur Motorbridge Web UI D-Bot démarré avec succès !")
    print(f"👉 Accès local Jetson : http://localhost:{args.port}")
    print(f"👉 Accès depuis le Mac: http://ubuntu.local:{args.port}  (ou IP Jetson)")
    print(f"========================================================\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur Web UI...")
        GLOBAL_STATE.disable()
        httpd.server_close()


if __name__ == '__main__':
    main()
