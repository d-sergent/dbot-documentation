#!/usr/bin/env python3
"""
scripts/vision/stream_camera.py — Serveur Web WebRTC/MJPEG pour OAK-D
======================================================================
Crée un serveur web local pour diffuser le flux vidéo de l'OAK-D Pro.
Utilise l'interface matérielle dbot.vision.oak_camera (DepthAI v2).
"""

import cv2
import threading
import time
from flask import Flask, Response
import sys
import os

# Ajouter le dossier Code à l'environnement Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from dbot.vision.oak_camera import DbotCamera

app = Flask(__name__)
cam = None

def generate_frames():
    """Générateur de flux JPEG pour le navigateur"""
    global cam
    while True:
        if cam is None:
            time.sleep(0.1)
            continue
            
        frame = cam.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue
            
        ret, buffer = cv2.imencode('.jpg', frame)
        if ret:
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    html = """
    <html>
        <head>
            <title>D-Bot Vision</title>
            <style>
                body { background-color: #1a1a1a; color: white; font-family: sans-serif; text-align: center; }
                h1 { margin: 20px; }
                img { border: 2px solid #333; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0,0,0,0.5); }
            </style>
        </head>
        <body>
            <h1>D-Bot : OAK-D Pro (Live)</h1>
            <img src="/video_feed" width="640" height="360" />
        </body>
    </html>
    """
    return html

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def main():
    global cam
    print("=" * 50)
    print("  D‑Bot — Serveur Streaming Vidéo")
    print("=" * 50)
    
    try:
        cam = DbotCamera(resolution="1080p", fps=30)
        cam.start()
        
        print("🚀 Lancement du serveur Web...")
        print("Sur votre Mac, ouvrez un navigateur web et allez sur :")
        print("👉 http://<adresse-ip-jetson>:5000")
        print("-" * 50)
        
        app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)
    except Exception as e:
        print(f"❌ Erreur : {e}")
    finally:
        if cam:
            cam.stop()

if __name__ == '__main__':
    main()
