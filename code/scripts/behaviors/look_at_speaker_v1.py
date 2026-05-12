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

from dbot.audio.audio_io_v2 import AudioIOv2
from dbot.vision.face_tracker import FaceTracker

class LookAtSpeakerDemo:
    def __init__(self):
        print("🤖 [D-Bot] Initialisation du système de fusion Audio-Vision...")
        
        # 1. Initialisation Vision
        self.tracker = FaceTracker()
        self.device = dai.Device(self.pipeline_builder()) # On utilise notre tracker
        
        # 2. Initialisation Audio
        self.last_doa_angle = None
        self.audio = AudioIOv2(doa_callback=self.on_doa_update)
        
        print("✅ [D-Bot] Système prêt. Parlez au robot pour tester.")

    def pipeline_builder(self):
        """Récupère le pipeline configuré du tracker."""
        return self.tracker.pipeline

    def on_doa_update(self, angle):
        """Callback appelé quand le ReSpeaker détecte une direction de voix."""
        self.last_doa_angle = angle
        print(f"\n👂 [Audio] Son détecté à l'angle : {angle}°")

    def run(self):
        """Boucle principale de démonstration."""
        print("👀 [D-Bot] En attente de détection...")
        
        try:
            while True:
                # 1. Récupération des visages depuis l'OAK-D
                faces, frame = self.tracker.run_detection(self.device)
                
                if faces:
                    # On prend le visage le plus central
                    f = faces[0]
                    print(f"👤 [Vision] Je vous vois ! Position : X={f['x']:.0f}mm, Z={f['z']:.0f}mm", end='\r')
                    
                    # Dessin sur l'image pour le feedback visuel
                    if frame is not None:
                        cv2.putText(frame, f"Visage: {f['z']/1000:.2f}m", (10, 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # 2. Affichage (si écran disponible)
                if frame is not None:
                    cv2.imshow("D-Bot Perception - Audio + Vision", frame)
                
                # 3. Sortie propre
                if cv2.waitKey(1) == ord('q'):
                    break
                    
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n🛑 Arrêt de la démonstration.")
        finally:
            self.device.close()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    demo = LookAtSpeakerDemo()
    demo.run()
