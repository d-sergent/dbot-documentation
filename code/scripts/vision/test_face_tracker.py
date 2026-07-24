"""
Script de Test et d'Enregistrement de Visages en Temps Réel pour D-Bot V1.

Usage :
1. Mode Reconnaissance en Temps Réel :
   python3 code/scripts/vision/test_face_tracker.py

2. Mode Enregistrement d'un nouveau profil (ex: 'David') :
   python3 code/scripts/vision/test_face_tracker.py --register "David"

Auteur : D-Bot Project (Google DeepMind Agentic Coding)
Date : 2026-07-24
"""

import os
import sys
import time
import argparse
import collections

# Protection Headless SSH : Configuration de Qt en mode offscreen si aucun écran X11 n'est présent
HAS_DISPLAY = bool(os.environ.get("DISPLAY"))
if not HAS_DISPLAY:
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

import cv2
import numpy as np

# Inclusion du chemin racine pour importer le package dbot
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
if CODE_ROOT not in sys.path:
    sys.path.insert(0, CODE_ROOT)

from dbot.vision.face_tracker import FaceTracker
from dbot.vision.yolo_world import YoloWorldDetector

try:
    from dbot.vision.oak_camera import DbotCamera
    OAK_AVAILABLE = True
except ImportError:
    OAK_AVAILABLE = False


import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# Structure partagée pour le serveur Web MJPEG
class WebState:
    def __init__(self):
        self.lock = threading.Lock()
        self.jpeg_frame = None
        self.register_trigger = False
        self.register_name = ""
        self.is_centered = False

GLOBAL_WEB = WebState()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Serveur HTTP multithreadé pour le streaming MJPEG."""
    daemon_threads = True


class MJPEGHandler(BaseHTTPRequestHandler):
    """Handler HTTP servant la page HTML et le flux MJPEG."""
    def log_message(self, format, *args):
        pass  # Silence les logs HTTP de routine

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <title>D-Bot Face Tracker Web UI</title>
                <style>
                    body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; margin: 0; padding: 20px; }
                    h1 { color: #38bdf8; font-size: 24px; margin-bottom: 10px; }
                    .card { background: #1e293b; border-radius: 12px; padding: 15px; display: inline-block; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
                    img { border-radius: 8px; max-width: 100%; height: auto; border: 2px solid #334155; }
                    .controls { margin-top: 15px; }
                    input[type="text"] { padding: 10px 15px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; font-size: 16px; width: 200px; }
                    button { padding: 10px 20px; border-radius: 6px; border: none; background: #0284c7; color: white; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; }
                    button:hover { background: #0369a1; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>👁️ D-Bot Face Tracker (Reconnaissance Faciale)</h1>
                    <img src="/video_feed" width="850" alt="Flux Vidéo D-Bot">
                    <div class="controls">
                        <form action="/api/register" method="GET" style="display:inline-block;">
                            <input type="text" name="name" placeholder="Prénom (ex: David)" required>
                            <button type="submit">📸 Enregistrer le Visage</button>
                        </form>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))

        elif self.path == '/video_feed':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                with GLOBAL_WEB.lock:
                    frame_bytes = GLOBAL_WEB.jpeg_frame
                if frame_bytes is not None:
                    try:
                        self.wfile.write(b'--frame\r\n')
                        self.send_header('Content-type', 'image/jpeg')
                        self.send_header('Content-length', str(len(frame_bytes)))
                        self.end_headers()
                        self.wfile.write(frame_bytes)
                        self.wfile.write(b'\r\n')
                    except Exception:
                        break
                time.sleep(0.033)  # ~30 FPS

        elif self.path.startswith('/api/register'):
            import urllib.parse
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            name = params.get('name', [''])[0].strip()
            if name:
                with GLOBAL_WEB.lock:
                    GLOBAL_WEB.register_trigger = True
                    GLOBAL_WEB.register_name = name
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()


def start_web_server(port=8090):
    server = ThreadedHTTPServer(('0.0.0.0', port), MJPEGHandler)
    print(f"🌐 [Web UI] Serveur déporté actif sur http://ubuntu.local:{port} (ou http://<IP_JETSON>:{port})")
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Test & Enregistrement Reconnaissance Faciale D-Bot")
    parser.add_argument("--register", type=str, default="", help="Nom de la personne à enregistrer (ex: 'David')")
    parser.add_argument("--reset", action="store_true", help="Effacer les anciens profils faciaux et recommencer à zéro")
    parser.add_argument("--threshold", type=float, default=0.30, help="Seuil de similarité cosinus (défaut: 0.30)")
    parser.add_argument("--port", type=int, default=8090, help="Port du serveur Web MJPEG (défaut: 8090)")
    parser.add_argument("--use-webcam", action="store_true", help="Forcer l'utilisation de la webcam au lieu de l'OAK-D")
    args = parser.parse_args()

    if args.reset:
        faces_json = os.path.abspath(os.path.join(SCRIPT_DIR, "../../dbot/vision/faces/known_faces.json"))
        if os.path.exists(faces_json):
            os.remove(faces_json)
            print("🗑️ [FaceTracker] Anciens profils faciaux supprimés. Démarrage de la base à zéro !")

    # Démarrage du thread Web Server
    web_thread = threading.Thread(target=start_web_server, args=(args.port,), daemon=True)
    web_thread.start()

    print("🚀 [FaceTracker Test] Initialisation du système de reconnaissance faciale ultra-compact...")
    tracker = FaceTracker(match_threshold=args.threshold)
    detector = YoloWorldDetector(classes=["personne"], default_conf_threshold=0.15)

    use_oak = OAK_AVAILABLE and not args.use_webcam
    cam = None

    if use_oak:
        print("⏳ [Vision] Initialisation de la caméra OAK-D Pro...")
        try:
            cam = DbotCamera()
            cam.start()
            print("✅ [Vision] Caméra OAK-D Pro opérationnelle.")
        except Exception as e:
            print(f"⚠️ Échec démarrage OAK-D Pro ({e}). Repli sur OpenCV VideoCapture...")
            use_oak = False

    if not use_oak:
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            print("❌ Erreur : Aucune caméra disponible (OAK-D ou Webcam).")
            sys.exit(1)
        print("✅ [Vision] Webcam OpenCV active.")

    register_mode = len(args.register.strip()) > 0
    target_name = args.register.strip().title()

    if register_mode:
        print(f"📸 [MODE ENREGISTREMENT] Positionnez le visage de '{target_name}' au centre du champ.")
        print("   Appuyez sur la touche 'SPACE' dans la fenêtre d'affichage (ou Ctrl+C) pour capturer et enregistrer.")
    else:
        print("🔍 [MODE RECONNAISSANCE] Inférence faciale active. Appuyez sur 'q' pour quitter.")

    # Buffer de lissage temporel : {track_key -> deque d'embeddings sur N frames}
    SMOOTH_N = 5
    emb_buffers = collections.defaultdict(lambda: collections.deque(maxlen=SMOOTH_N))

    try:
        while True:
            t0 = time.perf_counter()

            if use_oak:
                frame = cam.get_frame()
                spatial_dets = []
            else:
                ret, frame = cam.read()
                if not ret:
                    break
                spatial_dets = []

            if frame is None:
                continue

            h, w = frame.shape[:2]
            detections, latency_ms = detector.detect(frame)

            # Traitement des personnes détectées par YOLO-World
            for det_idx, det in enumerate(detections):
                if det["label"].upper() in ["PERSONNE", "PERSON"]:
                    bbox = det["bbox"]
                    x1, y1, x2, y2 = bbox

                    # Clé unique par position (zone de l'image) pour le buffer de lissage
                    track_key = f"{x1//100}_{y1//100}"

                    # === Lissage Temporel : moyenne des embeddings sur SMOOTH_N frames ===
                    # Extraction de l'embedding brut (sans identification)
                    h_tmp, w_tmp = frame.shape[:2]
                    head_h_tmp = int((y2 - y1) * 0.55)
                    hx1_t, hy1_t = max(0, x1), max(0, y1)
                    hx2_t, hy2_t = min(w_tmp, x2), min(h_tmp, y1 + head_h_tmp)
                    head_crop_tmp = frame[hy1_t:hy2_t, hx1_t:hx2_t]

                    face_bbox = (x1, y1, x2, y1 + head_h_tmp)  # Fallback bbox

                    if head_crop_tmp.size > 0:
                        faces_tmp = tracker.detect_faces_scrfd(head_crop_tmp, conf_thresh=0.35)
                        if faces_tmp:
                            best_tmp = max(faces_tmp, key=lambda f: f['score'])
                            bx1t, by1t, bx2t, by2t = best_tmp['bbox']
                            lmks_tmp = best_tmp['landmarks']
                            if lmks_tmp is not None and len(lmks_tmp) == 5:
                                aligned_tmp = tracker.align_face(head_crop_tmp, lmks_tmp)
                            else:
                                fr_tmp = head_crop_tmp[max(0,by1t):min(head_crop_tmp.shape[0],by2t),
                                                       max(0,bx1t):min(head_crop_tmp.shape[1],bx2t)]
                                aligned_tmp = cv2.resize(fr_tmp if fr_tmp.size > 0 else head_crop_tmp, (112, 112))
                            face_bbox = (max(0, hx1_t+bx1t), max(0, hy1_t+by1t),
                                         min(w_tmp, hx1_t+bx2t), min(h_tmp, hy1_t+by2t))
                        else:
                            ch_t, cw_t = head_crop_tmp.shape[:2]
                            fr_tmp = head_crop_tmp[int(ch_t*0.05):int(ch_t*0.90), int(cw_t*0.10):int(cw_t*0.90)]
                            aligned_tmp = cv2.resize(fr_tmp if fr_tmp.size > 0 else head_crop_tmp, (112, 112))
                            face_bbox = (max(0, hx1_t+int(cw_t*0.10)), max(0, hy1_t+int(ch_t*0.05)),
                                         min(w_tmp, hx1_t+int(cw_t*0.90)), min(h_tmp, hy1_t+int(ch_t*0.90)))

                        emb_tmp = tracker.get_embedding(aligned_tmp)
                        if np.linalg.norm(emb_tmp) > 0:
                            emb_buffers[track_key].append(emb_tmp)

                    # Identification sur l'embedding moyen lissé
                    if len(emb_buffers[track_key]) > 0:
                        mean_emb = np.mean(list(emb_buffers[track_key]), axis=0)
                        norm_me = np.linalg.norm(mean_emb)
                        if norm_me > 0:
                            mean_emb = mean_emb / norm_me
                        name, sim = tracker.identify_embedding(mean_emb)
                    else:
                        name, sim = "INCONNU", 0.0

                    fx1, fy1, fx2, fy2 = face_bbox

                    # Couleur : Vert si reconnu, Jaune si Inconnu
                    color = (0, 255, 0) if name != "INCONNU" else (0, 255, 255)
                    label_text = f"{name} ({sim*100:.0f}%)" if name != "INCONNU" else "PERSONNE INCONNUE"

                    # Dessin du rectangle exact autour du visage et de la bannière nominative
                    cv2.rectangle(frame, (fx1, fy1), (fx2, fy2), color, 2)
                    cv2.rectangle(frame, (fx1, max(0, fy1 - 30)), (fx1 + len(label_text) * 11, fy1), color, -1)
                    cv2.putText(frame, label_text, (fx1 + 5, max(15, fy1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

            # Réticule et Guide de Centrage Visuel en Mode Enregistrement
            if register_mode:
                cx, cy = w // 2, h // 2
                box_w, box_h = 240, 240
                rx1, ry1 = cx - box_w // 2, cy - box_h // 2
                rx2, ry2 = cx + box_w // 2, cy + box_h // 2

                # Vérification si la tête de la personne est dans la zone de visée centrale
                is_centered = False
                for det in detections:
                    if det["label"] == "PERSONNE":
                        bx1, by1, bx2, by2 = det["bbox"]
                        hx, hy = (bx1 + bx2) // 2, by1 + int((by2 - by1) * 0.20)
                        if rx1 <= hx <= rx2 and ry1 <= hy <= ry2:
                            is_centered = True
                            break

                target_color = (0, 255, 0) if is_centered else (0, 165, 255)
                # Dessin du cadre de centrage et de la croix centrale
                cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), target_color, 2)
                cv2.line(frame, (cx - 15, cy), (cx + 15, cy), target_color, 2)
                cv2.line(frame, (cx, cy - 15), (cx, cy + 15), target_color, 2)

                if is_centered:
                    status_str = f"✅ VISAGE DE '{target_name}' CENTRÉ - APPUYEZ SUR ESPACE"
                    cv2.putText(frame, status_str, (30, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
                    print(f"\r✅ [CENTRÉ] Visage de '{target_name}' au milieu ! Appuyez sur ESPACE pour capturer.", end="", flush=True)
                else:
                    status_str = f"➡️ RECENTRER LE VISAGE DE '{target_name}' DANS LE CADRE VERT"
                    cv2.putText(frame, status_str, (30, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 165, 255), 2)
                    print(f"\r➡️ [CADRAGE] Recentre le visage au milieu du champ...", end="", flush=True)

            t1 = time.perf_counter()
            fps = 1.0 / max(0.001, t1 - t0)

            cv2.putText(frame, f"FPS: {fps:.1f} | Latence Vision: {latency_ms:.1f}ms", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Encodage JPEG pour le serveur Web MJPEG (http://ubuntu.local:8090)
            ret_jpg, jpeg_buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if ret_jpg:
                with GLOBAL_WEB.lock:
                    GLOBAL_WEB.jpeg_frame = jpeg_buf.tobytes()

            # Enregistrement périodique d'une image témoin sur disque
            cv2.imwrite("/tmp/face_tracker_snapshot.jpg", frame)

            key = 0
            if HAS_DISPLAY:
                try:
                    cv2.imshow("D-Bot Face Tracker", frame)
                    key = cv2.waitKey(1) & 0xFF
                except Exception:
                    pass

            # Déclenchement de la capture depuis le Web UI ou la touche ESPACE
            web_req = False
            web_name = ""
            with GLOBAL_WEB.lock:
                if GLOBAL_WEB.register_trigger:
                    web_req = True
                    web_name = GLOBAL_WEB.register_name
                    GLOBAL_WEB.register_trigger = False

            if key == ord('q'):
                break
            elif (register_mode and key == 32) or web_req:  # Touche ESPACE ou Bouton Web UI
                reg_name = web_name if web_req else target_name
                if not reg_name:
                    reg_name = "David"
                # Capture et enregistrement du visage via pipeline SCRFD complet
                for det in detections:
                    if det["label"].upper() in ["PERSONNE", "PERSON"]:
                        x1, y1, x2, y2 = det["bbox"]
                        head_h = int((y2 - y1) * 0.55)
                        head_crop = frame[max(0, y1):min(y1 + head_h, h), max(0, x1):min(x2, w)]
                        if head_crop.size > 0:
                            # Pipeline SCRFD : détection visage exacte + alignement ArcFace
                            faces = tracker.detect_faces_scrfd(head_crop, conf_thresh=0.35)
                            if faces:
                                best = max(faces, key=lambda f: f['score'])
                                lmks = best['landmarks']
                                if lmks is not None and len(lmks) == 5:
                                    aligned = tracker.align_face(head_crop, lmks)
                                else:
                                    bx1, by1, bx2, by2 = best['bbox']
                                    face_roi = head_crop[max(0,by1):min(head_crop.shape[0],by2),
                                                         max(0,bx1):min(head_crop.shape[1],bx2)]
                                    aligned = cv2.resize(face_roi if face_roi.size > 0 else head_crop, (112, 112))
                            else:
                                # Fallback anatomique si SCRFD ne détecte rien
                                ch, cw = head_crop.shape[:2]
                                face_roi = head_crop[int(ch*0.05):int(ch*0.90), int(cw*0.10):int(cw*0.90)]
                                aligned = cv2.resize(face_roi if face_roi.size > 0 else head_crop, (112, 112))

                            success = tracker.register_face(reg_name, aligned)
                            if success:
                                print(f"\n🎉 [Web UI / Console] Enregistrement réussi pour '{reg_name}' !")
                                register_mode = False
                                break

    except KeyboardInterrupt:
        print("\n🛑 Arrêt par l'utilisateur.")
    finally:
        if use_oak and cam:
            cam.stop()
        elif cam:
            cam.release()
        cv2.destroyAllWindows()
        print("✅ Ressources nettoyées.")


if __name__ == "__main__":
    main()
