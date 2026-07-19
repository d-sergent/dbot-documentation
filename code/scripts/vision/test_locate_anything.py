#!/usr/bin/env python3
"""
scripts/vision/test_locate_anything.py — Test d'inférence LocateAnything-3B (W4A16 INT4 / FP16)
==================================================================================================
Capture une frame via OAK-D Pro (DbotCamera), charge LocateAnything pré-quantifié W4A16 (AWQ)
pour limiter l'empreinte VRAM à ~1.8 Go sur la Jetson Orin Nano (8 Go), et extrait la bounding box 2D.

Usage:
    python3 scripts/vision/test_locate_anything.py --prompt "a phone"
"""

import os
# --- Configuration environnement PyTorch Jetson Tegra (Désactivation NVML) ---
os.environ["PYTORCH_NVML_BASED_CUDA_CHECK"] = "0"
os.environ["TORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"

import sys
import time
import argparse
import traceback
import types
import importlib.machinery
from unittest.mock import MagicMock

# --- Astuce Jetson ARM64 : MagicMock dynamique pour 'decord' et 'torchvision' ---
try:
    import decord
except ImportError:
    decord_mock = MagicMock()
    decord_mock.__spec__ = importlib.machinery.ModuleSpec("decord", None)
    sys.modules["decord"] = decord_mock

try:
    import torchvision
except (ImportError, RuntimeError):
    tv_mock = MagicMock()
    tv_mock.__spec__ = importlib.machinery.ModuleSpec("torchvision", None)
    sys.modules["torchvision"] = tv_mock
    sys.modules["torchvision.io"] = tv_mock.io
    sys.modules["torchvision.transforms"] = tv_mock.transforms
    sys.modules["torchvision.transforms.functional"] = tv_mock.transforms.functional

import cv2
import numpy as np
import torch
from PIL import Image

# Ajouter le dossier Code au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from dbot.vision.oak_camera import DbotCamera

DEFAULT_PROMPT = "a phone"
# Modèle optimisé 4-bit AWQ (~1.8 Go VRAM) idéal pour Jetson Orin 8 Go
DEFAULT_MODEL = "sahilchachra/LocateAnything-3B-AWQ-W4A16"
OUTPUT_PATH = "/tmp/locate_anything_result.jpg"

def main():
    parser = argparse.ArgumentParser(description="Test LocateAnything-3B sur Jetson Orin Nano")
    parser.add_argument("--prompt", type=str, default=DEFAULT_PROMPT, help="Texte ou objet à localiser")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="ID du dépôt Hugging Face du modèle")
    args = parser.parse_args()

    print("=" * 60)
    print(f"  D‑Bot — Test Visual Grounding : LocateAnything-3B (AWQ 4-bit)")
    print(f"  Dépôt : {args.model}")
    print("=" * 60)

    # 1. Capture Image OAK-D Pro
    print("\n📷 [1/3] Capture d'une image via OAK-D Pro...")
    cam = None
    frame = None
    try:
        cam = DbotCamera(resolution="1080p", fps=30)
        cam.start()
        
        # Temps de chauffe auto-exposition
        for _ in range(15):
            frame = cam.get_frame()
            time.sleep(0.05)
            
        if frame is None:
            print("❌ Erreur : Impossible de capturer une image depuis la caméra OAK-D.")
            sys.exit(1)
            
        print(f"  ✅ Image capturée avec succès : {frame.shape[1]}x{frame.shape[0]} px")
    except Exception as e:
        print(f"❌ Erreur caméra : {e}")
        sys.exit(1)
    finally:
        if cam:
            cam.stop()

    # Convertir BGR (OpenCV) vers RGB (PIL)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_frame)

    # 2. Chargement du modèle AWQ 4-bit
    print(f"\n🧠 [2/3] Chargement du modèle {args.model} en VRAM (~1.8 Go)...")
    t0_load = time.time()

    try:
        import transformers
        print(f"  📦 Version de transformers installée : {transformers.__version__}")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"  ⚡ Périphérique d'exécution : {device.upper()}")
        
        if torch.cuda.is_available():
            torch.cuda.set_per_process_memory_fraction(0.95)
            torch.cuda.empty_cache()
        
        dtype = torch.float16
        kwargs = {"dtype": dtype, "low_cpu_mem_usage": False}

        from transformers import AutoProcessor, AutoModel
        processor = AutoProcessor.from_pretrained(args.model, trust_remote_code=True)
        
        print("  🚚 Instanciation du modèle sur le GPU CUDA...")
        model = AutoModel.from_pretrained(
            args.model,
            trust_remote_code=True,
            **kwargs
        )
        
        if "device_map" not in kwargs:
            model = model.to("cuda")
        
        load_duration = time.time() - t0_load
        print(f"  ✅ Modèle chargé avec succès en {load_duration:.2f}s !")
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement du modèle : {e}")
        print("\n--- Traceback détaillé ---")
        traceback.print_exc()
        print("---------------------------\n")
        sys.exit(1)

    # 3. Inférence & Extraction Bounding Box
    print(f"\n🔍 [3/3] Inférence avec le prompt : '{args.prompt}'...")
    t0_infer = time.time()

    try:
        inputs = processor(text=args.prompt, images=pil_image, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=100)
        result_text = processor.decode(outputs[0], skip_special_tokens=True)
            
        infer_duration = time.time() - t0_infer
        
        print(f"  ⏱️ Inférence terminée en {infer_duration:.3f}s !")
        print(f"  📝 Résultat brut : {result_text}")

        # Incrustation sur l'image
        cv2.putText(frame, f"Prompt: {args.prompt} ({infer_duration:.2f}s)", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        cv2.imwrite(OUTPUT_PATH, frame)
        print(f"\n✅ Image de résultat sauvegardée dans : {OUTPUT_PATH}")

    except Exception as e:
        print(f"❌ Erreur pendant l'inférence : {e}")
        sys.exit(1)

    print("\n🎉 Test Étape 1 terminé avec succès !")

if __name__ == "__main__":
    main()
