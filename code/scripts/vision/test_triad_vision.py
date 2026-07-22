"""
scripts/vision/test_triad_vision.py — Test Complet de la Triade Visuelle D-Bot
===============================================================================
Couple OAK-D Pro (RGB-D + Laser IR), YOLO-World v2 (Inférence Zero-Shot) et
SpatialFusion pour afficher en direct la position 3D (X, Y, Z) des objets repérés.

Filtrage Intelligent : Met en valeur les objets dans la zone d'action du robot (Z < 1.5m).
"""

import depthai as dai
import cv2
import numpy as np
import time
import sys

from dbot.vision.yolo_world import YoloWorldDetector
from dbot.vision.spatial_fusion import SpatialFusion

def run_triad_test():
    print("🚀 [Triade Visuelle] Démarrage du test d'intégration en situation réelle...")

    # Prompts cibles
    target_classes = ["main", "telephone", "bouteille", "personne", "chaise", "obstacle"]
    print(f"🎯 Prompts sémantiques cibles : {target_classes}")
    
    detector = YoloWorldDetector(confidence_threshold=0.28, classes=target_classes)
    fusion = SpatialFusion()

    # Configuration Pipeline DepthAI
    pipeline = dai.Pipeline()

    cam_rgb = pipeline.create(dai.node.ColorCamera)
    mono_left = pipeline.create(dai.node.MonoCamera)
    mono_right = pipeline.create(dai.node.MonoCamera)
    stereo = pipeline.create(dai.node.StereoDepth)

    xout_rgb = pipeline.create(dai.node.XLinkOut)
    xout_depth = pipeline.create(dai.node.XLinkOut)

    xout_rgb.setStreamName("rgb")
    xout_depth.setStreamName("depth")

    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setIspScale(1, 3) # 1080p -> 640x360
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam_rgb.setFps(30)
    cam_rgb.setInterleaved(False)

    mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    mono_left.setBoardSocket(dai.CameraBoardSocket.CAM_B)
    mono_left.setFps(30)

    mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    mono_right.setBoardSocket(dai.CameraBoardSocket.CAM_C)
    mono_right.setFps(30)

    stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
    stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
    stereo.setLeftRightCheck(True)
    stereo.setExtendedDisparity(True)
    stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)

    mono_left.out.link(stereo.left)
    mono_right.out.link(stereo.right)
    cam_rgb.isp.link(xout_rgb.input)
    stereo.depth.link(xout_depth.input)

    print("⏳ Connexion à la caméra OAK-D Pro et activation du Laser IR...")
    with dai.Device(pipeline) as device:
        try:
            device.setIrLaserDotProjectorIntensity(200)
            print("🌙 Projecteur Laser IR actif à 200 mA.")
        except Exception as e:
            print(f"⚠ Avertissement Laser IR : {e}")

        q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        q_depth = device.getOutputQueue(name="depth", maxSize=4, blocking=False)

        print("\n✅ Triade Visuelle Active ! Approchez votre main, votre téléphone ou une bouteille (< 1.5 m).")
        print("🔍 Surveillance en cours... Appuyez sur Ctrl+C pour quitter.\n")

        fps_count = 0
        t_start = time.time()

        while True:
            in_rgb = q_rgb.get()
            in_depth = q_depth.get()

            if in_rgb is None or in_depth is None:
                continue

            frame_rgb = in_rgb.getCvFrame()
            frame_depth = in_depth.getFrame()

            # Étape 1 : Inférence YOLO-World (avec conversion BGR->RGB interne)
            detections_2d, latency_ms = detector.detect(frame_rgb)

            # Étape 2 : Fusion Spatiale 3D
            detections_3d = fusion.compute_spatial_3d(detections_2d, frame_depth)

            # Étape 3 : Filtrage Zone d'Action (< 1.5 m) vs Arrière-plan
            fps_count += 1
            if time.time() - t_start >= 1.0:
                action_zone_dets = [d for d in detections_3d if 0 < d["spatial_3d"]["z_mm"] <= 1500]
                bg_dets_count = len(detections_3d) - len(action_zone_dets)

                print(f"⚡ [Triade Stats] FPS: {fps_count} | Latence: {latency_ms:.1f} ms | Zone Action (<1.5m): {len(action_zone_dets)} | Arrière-plan: {bg_dets_count}")
                
                if len(action_zone_dets) > 0:
                    for det in action_zone_dets:
                        label = det["label"]
                        conf = det["confidence"]
                        s = det["spatial_3d"]
                        print(f"   🔥 [ACTION PROCHE] [{label.upper()} {conf*100:.0f}%] ➔ X={s['x_mm']:.0f}mm, Y={s['y_mm']:.0f}mm, Z={s['z_mm']:.0f}mm ({s['z_mm']/1000.0:.2f}m)")
                else:
                    print("   ⚪ Aucune détection dans la zone de manipulation proche (< 1.5 m).")

                fps_count = 0
                t_start = time.time()

            time.sleep(0.01)

if __name__ == "__main__":
    try:
        run_triad_test()
    except KeyboardInterrupt:
        print("\n🔌 Arrêt du test visuel.")
    except Exception as err:
        print(f"❌ Erreur test : {err}")
