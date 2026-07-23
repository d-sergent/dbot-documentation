"""
scripts/vision/test_oak_tracker.py — Test Unitaire du Nœud VPU ObjectTracker OAK-D Pro
====================================================================================
Vérifie la création et l'exécution du nœud matériel dai.node.ObjectTracker sur le VPU Myriad X.
Mesure la fréquence de rafraîchissement des tracklets matériels (cible : 60+ FPS).

Exécution sur la Jetson / Mac :
    python3 code/scripts/vision/test_oak_tracker.py
"""

import depthai as dai
import cv2
import time
import sys

def test_vpu_object_tracker():
    print("⏳ [Test Unitaire 1] Construction du pipeline DepthAI avec ObjectTracker VPU...")
    pipeline = dai.Pipeline()

    # 1. Capteur RGB 1080p -> 640x360 via ISP (81° FOV)
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setIspScale(1, 3)
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam_rgb.setFps(60)

    # 2. Sortie Vidéo ISP
    xout_video = pipeline.create(dai.node.XLinkOut)
    xout_video.setStreamName("video")
    cam_rgb.isp.link(xout_video.input)

    # 3. Nœud Matériel ObjectTracker sur VPU Myriad X
    tracker = pipeline.create(dai.node.ObjectTracker)
    tracker.setTrackerType(dai.TrackerType.ZERO_TILT)
    tracker.setTrackerIdAssignmentPolicy(dai.TrackerIdAssignmentPolicy.SMALLEST_ID)

    # Relier le flux vidéo au tracker VPU
    cam_rgb.video.link(tracker.inputTrackerFrame)

    # Sortie Tracklets matériels
    xout_tracker = pipeline.create(dai.node.XLinkOut)
    xout_tracker.setStreamName("tracklets")
    tracker.out.link(xout_tracker.input)

    print("⏳ Démarrage du device OAK-D Pro...")
    with dai.Device(pipeline) as device:
        video_q = device.getOutputQueue(name="video", maxSize=4, blocking=False)
        tracker_q = device.getOutputQueue(name="tracklets", maxSize=4, blocking=False)

        print("✅ Pipeline VPU actif ! Mesure de fréquence du tracker matériel sur 5 secondes...")
        
        t_start = time.perf_counter()
        frame_count = 0
        tracker_count = 0

        while time.perf_counter() - t_start < 5.0:
            if video_q.has():
                _ = video_q.get()
                frame_count += 1

            if tracker_q.has():
                t_data = tracker_q.get()
                tracklets = t_data.tracklets
                tracker_count += 1
                if tracker_count % 30 == 0:
                    print(f"📊 [VPU Tracker] Paquet #{tracker_count} reçu | Active Tracklets: {len(tracklets)}")

            time.sleep(0.005)

        elapsed = time.perf_counter() - t_start
        fps_video = frame_count / elapsed
        fps_tracker = tracker_count / elapsed

        print("\n========================================================")
        print(f"🎯 RÉSULTATS TEST UNITAIRE 1 (VPU ObjectTracker)")
        print(f"   • Cadence Vidéo ISP : {fps_video:.1f} FPS")
        print(f"   • Cadence Tracker VPU : {fps_tracker:.1f} FPS")
        print("========================================================\n")
        assert fps_tracker > 30, "La cadence du tracker doit être > 30 FPS !"
        print("✅ [Test Unitaire 1] VALIDE avec succès !")

if __name__ == "__main__":
    try:
        test_vpu_object_tracker()
    except Exception as e:
        print(f"❌ Échec Test Unitaire 1 : {e}")
        sys.exit(1)
