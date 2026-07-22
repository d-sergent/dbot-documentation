#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/vision/server_active_gaze_mac.py — Serveur Compagnon Visual Grounding pour Mac M1 Max
=============================================================================================
Serveur HTTP léger (Port 8090) exécuté sur le Mac M1 Max pour la perception visuelle complexe
et le Visual Grounding (LocateAnything-3B / VLM / YOLO-World Bridge).

Exécution sur le Mac :
    /opt/homebrew/bin/python3.11 code/scripts/vision/server_active_gaze_mac.py --port 8090
"""

import sys
import os
import json
import base64
import time
import cv2
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# ── Serveur HTTP Multithread ───────────────────────────────

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class ActiveGazeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Désactiver les logs HTTP verbeux
        pass

    def send_json(self, data, code=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        t0 = time.perf_counter()
        if self.path == '/locate':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_json({"status": "error", "message": "Body vide"}, 400)
                return

            try:
                raw_body = self.rfile.read(content_length)
                req_data = json.loads(raw_body.decode('utf-8'))
                
                img_b64 = req_data.get("image_base64", "")
                prompt = req_data.get("prompt", "object").strip().lower()

                if not img_b64:
                    self.send_json({"status": "error", "message": "Image base64 requise"}, 400)
                    return

                # Décodage de l'image JPEG BGR
                img_bytes = base64.b64decode(img_b64)
                np_arr = np.frombuffer(img_bytes, np.uint8)
                frame_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame_bgr is None:
                    self.send_json({"status": "error", "message": "Impossible de décoder l'image"}, 400)
                    return

                h, w = frame_bgr.shape[:2]

                # ── Simulation / Inférence Visual Grounding ──
                # Dans un déploiement réel avec LocateAnything-3B / Qwen2.5-VL, l'inférence tourne ici sur le GPU du Mac.
                # Pour le pipeline de test gRPC/HTTP, on retourne la Bounding Box normalisée [x1, y1, x2, y2] dans [0.0, 1.0].
                
                t1 = time.perf_counter()
                latency_ms = (t1 - t0) * 1000.0

                print(f"👁️ [Mac ActiveGaze] Traitement prompt='{prompt}' sur trame {w}x{h} ({latency_ms:.1f} ms)")

                # Bounding box factice normalisée centrée ou décalée pour test
                res_bbox_norm = [0.35, 0.30, 0.65, 0.70] # [x1_rel, y1_rel, x2_rel, y2_rel]

                self.send_json({
                    "status": "success",
                    "prompt": prompt,
                    "bbox_norm": res_bbox_norm,
                    "target_center_norm": [0.50, 0.50],
                    "latency_ms": round(latency_ms, 1)
                })

            except Exception as e:
                print(f"❌ Erreur traitement /locate: {e}")
                self.send_json({"status": "error", "message": str(e)}, 500)
        else:
            self.send_error(404, "Endpoint non trouvé")

def main():
    port = 8090
    server_address = ('0.0.0.0', port)
    httpd = ThreadedHTTPServer(server_address, ActiveGazeHandler)
    print("\n========================================================")
    print(f"🚀 Serveur Compagnon Visual Grounding (Mac M1 Max) prêt !")
    print(f"👉 Adresse d'écoute : http://0.0.0.0:{port}/locate")
    print("========================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur Mac ActiveGaze...")
        httpd.server_close()

if __name__ == '__main__':
    main()
