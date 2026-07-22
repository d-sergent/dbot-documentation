"""
scripts/vision/export_yolo_tensorrt.py — Exporteur TensorRT FP16 pour YOLO-World v2
=====================================================================================
Compile le modèle PyTorch 'yolov8m-worldv2.pt' en un moteur TensorRT FP16 'yolov8m-worldv2.engine'
optimisé pour le GPU NVIDIA Ampere de la Jetson Orin Nano.

Empreinte mémoire : FP16 divise par 2 la taille des tenseurs et supprime le graphe autograd PyTorch,
réduisant l'empreinte VRAM à < 1.2 GB sur les 8 GB de la Jetson.
"""

import os
import sys
import time

def export_tensorrt(model_name="yolov8m-worldv2.pt"):
    print(f"🚀 [TensorRT Export] Début de la compilation TensorRT FP16 pour Jetson Orin Nano...")
    print(f"📦 Modèle source : '{model_name}'")
    
    try:
        from ultralytics import YOLOWorld
    except ImportError:
        print("❌ Erreur : Ultralytics n'est pas installé sur cet environnement.")
        sys.exit(1)

    print(f"⏳ Chargement des poids PyTorch '{model_name}'...")
    model = YOLOWorld(model_name)

    print("⚡ Lancement de l'exportation TensorRT (format='engine', half=True, device=0)...")
    print("   (Note : La compilation TensorRT effectue le tuning des kernels GPU et peut prendre 3 à 8 minutes sur la Jetson).")
    
    t0 = time.time()
    try:
        engine_path = model.export(
            format="engine",
            half=True,       # Inférence FP16 pour maîtriser l'empreinte VRAM (< 1.2 GB)
            device=0,        # GPU CUDA Jetson Orin Nano
            workspace=2      # Limite l'espace de mémoire temporaire de build à 2 GB
        )
        t1 = time.time()
        print(f"\n✅ [TensorRT Export] Exportation réussie en {t1-t0:.1f} secondes !")
        print(f"🎯 Moteur TensorRT prêt : '{engine_path}'")
    except Exception as e:
        print(f"❌ Échec de la compilation TensorRT : {e}")

if __name__ == "__main__":
    target_model = sys.argv[1] if len(sys.argv) > 1 else "yolov8m-worldv2.pt"
    export_tensorrt(target_model)
