#!/usr/bin/env python3
"""
scripts/vision/stream_camera.py — Serveur Web WebRTC/MJPEG pour OAK-D
======================================================================
Crée un serveur web local pour diffuser le le flux vidéo de l'OAK-D Pro.
Permet de visualiser la caméra depuis un navigateur web (ex: depuis le Mac).

Usage:
    python3 scripts/vision/stream_camera.py
    
Puis sur le Mac (dans un navigateur web) :
    http://<ip-de-la-jetson>:5000
"""

import cv2
import depthai as dai
import threading
import time
from flask import Flask, Response

app = Flask(__name__)
global_frame = None
lock = threading.Lock()

def camera_thread():
    """Thread dédié à la lecture du flux DepthAI"""
    global global_frame
    
    print("Initialisation du pipeline DepthAI...")
    try:
        with dai.Pipeline() as pipeline:
            # Création de la caméra
            cam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A)
            video_out = cam.requestOutput((640, 360), dai.ImgFrame.Type.BGR888p)
            queue = video_out.createOutputQueue()
            
            pipeline.start()
            print("✅ Caméra connectée ! Démarrage du flux HTTP...")
            
            # Temps de chauffe
            for _ in range(30):
                queue.get()
                
            while pipeline.isRunning():
                frame = queue.get().getCvFrame()
                # On encode le frame en JPEG pour l'envoyer sur le réseau
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    with lock:
                        global_frame = buffer.tobytes()
                        
    except Exception as e:
        print(f"❌ Erreur caméra : {e}")

def generate_frames():
    """Générateur de flux JPEG pour le navigateur"""
    global global_frame
    while True:
        with lock:
            frame = global_frame
        
        if frame is None:
            time.sleep(0.1)
            continue
            
        # Format "multipart/x-mixed-replace" (MJPEG)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """Page d'accueil simple affichant le flux vidéo"""
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
    """Route diffusant le flux d'images"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def main():
    print("=" * 50)
    print("  D‑Bot — Serveur Streaming Vidéo")
    print("=" * 50)
    
    # 1. Démarrage du thread caméra en arrière-plan
    t = threading.Thread(target=camera_thread)
    t.daemon = True
    t.start()
    
    # 2. Démarrage du serveur web sur le port 5000 (accessible à tout le réseau)
    print("🚀 Lancement du serveur Web...")
    print("Sur votre Mac, ouvrez un navigateur web et allez sur :")
    print("👉 http://<adresse-ip-jetson>:5000")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)

if __name__ == '__main__':
    main()
