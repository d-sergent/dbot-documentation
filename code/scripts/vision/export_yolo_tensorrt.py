"""
scripts/vision/export_yolo_tensorrt.py — Exporteur TensorRT & ONNX FP16 pour YOLO-World v2
==========================================================================================
Compile le modèle PyTorch 'yolov8m-worldv2.pt' en un moteur TensorRT / ONNX FP16
optimisé pour la Jetson Orin Nano avec détection dynamique du device CUDA.
"""

import os
import sys
import time
import torch

def export_tensorrt(model_name="yolov8m-worldv2.pt"):
    print(f"🚀 [TensorRT / ONNX Export] Début du processus de compilation pour Jetson Orin Nano...")
    print(f"📦 Modèle source : '{model_name}'")
    
    cuda_ok = torch.cuda.is_available()
    device_target = 0 if cuda_ok else "cpu"
    print(f"🖥 CUDA disponible : {cuda_ok} (Device cible : {device_target})")

    if not cuda_ok:
        print("⚠ Note JetPack : PyTorch est actuellement sur backend CPU.")
        print("  Si vous souhaitez l'accélération GPU maximale, réinstallez le wheel NVIDIA JetPack (torch-2.X+nv).")

    try:
        from ultralytics import YOLOWorld
    except ImportError:
        print("❌ Erreur : Ultralytics n'est pas installé sur cet environnement.")
        sys.exit(1)

    print(f"⏳ Chargement des poids PyTorch '{model_name}'...")
    model = YOLOWorld(model_name)

    fmt_export = "engine" if cuda_ok else "onnx"
    print(f"⚡ Lancement de l'exportation (format='{fmt_export}', device={device_target})...")
    
    t0 = time.time()
    try:
        if cuda_ok:
            engine_path = model.export(
                format="engine",
                half=True,
                device=0,
                workspace=2
            )
        else:
            engine_path = model.export(
                format="onnx",
                dynamic=True,
                device="cpu"
            )
        t1 = time.time()
        print(f"\n✅ [Export] Opération réussie en {t1-t0:.1f} secondes !")
        print(f"🎯 Fichier créé : '{engine_path}'")
    except Exception as e:
        print(f"❌ Échec de l'exportation : {e}")

if __name__ == "__main__":
    target_model = sys.argv[1] if len(sys.argv) > 1 else "yolov8m-worldv2.pt"
    export_tensorrt(target_model)
