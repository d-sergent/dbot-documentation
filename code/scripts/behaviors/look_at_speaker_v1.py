"""
scripts/behaviors/look_at_speaker_v1.py — Démonstration Audio-Vision
====================================================================
Combine le DOA (ReSpeaker) et le Face Tracking (OAK-D) pour localiser
l'utilisateur qui parle.
"""

import sys
import os
import time
import cv2
import depthai as dai

# Ajout du chemin racine pour l'import des modules dbot
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from flask import Flask, Response
from dbot.audio.audio_io_v2 import AudioIOv2
from dbot.vision.face_tracker import FaceTracker

app = Flask(__name__)
global_frame = None
global_faces = []
lock = threading.Lock()

class LookAtSpeakerDemo:
    def __init__(self):
        print("🤖 [D-Bot] Initialisation du système de fusion Audio-Vision...")
        self.display_mode = "--no-display" not in sys.argv
        self.web_mode = "--web" in sys.argv
        
        # 1. Initialisation Vision
        self.tracker = FaceTracker()
        try:
            self.device = dai.Device(self.tracker.pipeline)
        except Exception as e:
            print(f"❌ [Vision] Erreur OAK-D : {e}. Vérifiez le branchement.")
            sys.exit(1)
        
        # 2. Initialisation Audio
        self.last_doa_angle = None
        self.audio = AudioIOv2(doa_callback=self.on_doa_update)
        
        mode_str = "WEB" if self.web_mode else ("VISUEL" if self.display_mode else "CONSOLE")
        print(f"✅ [D-Bot] Système prêt (Mode: {mode_str}).")

    def on_doa_update(self, angle):
        self.last_doa_angle = angle
        print(f"\n👂 [Audio] Son détecté à : {angle}°")

    def run_loop(self):
        """Boucle de capture pour alimenter le serveur web ou l'affichage local."""
        global global_frame, global_faces
        try:
            while True:
                faces, frame = self.tracker.run_detection(self.device)
                
                if frame is not None:
                    # Dessin des infos IA sur l'image
                    for f in faces:
                        # Dessin simple d'un point au centre pour confirmer
                        cv2.circle(frame, (320, 180), 5, (0, 255, 0), -1)
                        cv2.putText(frame, f"Face: {f['z']/1000:.2f}m", (10, 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Mise à jour globale pour le Web
                    with lock:
                        global_faces = faces
                        ret, buffer = cv2.imencode('.jpg', frame)
                        if ret:
                            global_frame = buffer.tobytes()

                # Affichage local (si mode visuel classique)
                if self.display_mode and not self.web_mode and frame is not None:
                    cv2.imshow("D-Bot Vision", frame)
                    if cv2.waitKey(1) == ord('q'): break
                
                if not self.display_mode and not self.web_mode:
                    if faces:
                        f = faces[0]
                        print(f"👤 [Vision] Vu à Z={f['z']:.0f}mm", end='\r')
                    time.sleep(0.01)

        finally:
            self.device.close()

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            with lock:
                if global_frame is None:
                    time.sleep(0.1)
                    continue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n')
            time.sleep(0.05)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '<html><body><h1>D-Bot Vision Live</h1><img src="/video_feed" width="640"></body></html>'

if __name__ == "__main__":
    demo = LookAtSpeakerDemo()
    if "--web" in sys.argv:
        # Lancement du thread de capture
        t = threading.Thread(target=demo.run_loop, daemon=True)
        t.start()
        print("🚀 Serveur Web actif sur http://<IP_JETSON>:5000")
        app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)
    else:
        demo.run_loop()
