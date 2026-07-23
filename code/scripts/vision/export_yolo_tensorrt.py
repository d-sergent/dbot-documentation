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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
VISION_DIR = os.path.join(CODE_DIR, "dbot", "vision")

def export_tensorrt(model_name="yolov8m-worldv2.pt"):
    pt_path = os.path.join(VISION_DIR, model_name) if not os.path.isabs(model_name) else model_name
    print(f"🚀 [TensorRT / ONNX Export] Début du processus de compilation pour Jetson Orin Nano...")
    print(f"📦 Modèle source : '{pt_path}'")
    
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

    print(f"⏳ Chargement des poids PyTorch '{pt_path}'...")
    model = YOLOWorld(pt_path)

    fmt_export = "engine" if cuda_ok else "onnx"
    print(f"⚡ Lancement de l'exportation dans '{VISION_DIR}' (format='{fmt_export}', device={device_target})...")
    
    t0 = time.time()
    try:
        # Déplacement temporaire dans le répertoire vision pour que l'export y soit généré
        orig_cwd = os.getcwd()
        os.chdir(VISION_DIR)
        
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
        os.chdir(orig_cwd)
        t1 = time.time()
        print(f"\n✅ [Export] Opération réussie en {t1-t0:.1f} secondes !")
        print(f"🎯 Fichier créé dans : '{engine_path}'")
    except Exception as e:
        print(f"❌ Échec de l'exportation : {e}")

if __name__ == "__main__":
    target_model = sys.argv[1] if len(sys.argv) > 1 else "yolov8m-worldv2.pt"
    export_tensorrt(target_model)
