#!/usr/bin/env python3
"""
scripts/vision/test_locate_anything.py — Test d'inférence LocateAnything-3B (INT4/FP16)
========================================================================================
Capture une frame via OAK-D Pro (DbotCamera), charge LocateAnything en précision 
réduite (FP16/INT4) pour économiser la VRAM sur la Jetson Orin Nano, et extrait
la bounding box 2D de l'objet spécifié.

Usage:
    python3 scripts/vision/test_locate_anything.py --prompt "a red cup" --precision int4
"""

import sys
import os
import time
import argparse
import cv2
import numpy as np
import torch
from PIL import Image

# Ajouter le dossier Code au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from dbot.vision.oak_camera import DbotCamera

DEFAULT_PROMPT = "a cup"
MODEL_ID = "nvidia/LocateAnything-3B"
OUTPUT_PATH = "/tmp/locate_anything_result.jpg"

def main():
    parser = argparse.ArgumentParser(description="Test LocateAnything-3B sur Jetson Orin Nano")
    parser.add_argument("--prompt", type=str, default=DEFAULT_PROMPT, help="Texte ou objet à localiser")
    parser.add_argument("--precision", type=str, choices=["fp16", "int4"], default="fp16", help="Mode de quantification GPU")
    args = parser.parse_args()

    print("=" * 60)
    print(f"  D‑Bot — Test Visual Grounding : LocateAnything-3B ({args.precision.upper()})")
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

    # 2. Chargement du modèle quantifié
    print(f"\n🧠 [2/3] Chargement du modèle {MODEL_ID} en mode {args.precision.upper()}...")
    t0_load = time.time()
    
    use_pipeline = False
    pipe = None
    processor = None
    model = None

    try:
        import transformers
        print(f"  📦 Version de transformers installée : {transformers.__version__}")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"  ⚡ Périphérique d'exécution : {device.upper()}")
        
        dtype = torch.float16
        kwargs = {"torch_dtype": dtype, "device_map": "auto"}
        
        if args.precision == "int4":
            try:
                from transformers import BitsAndBytesConfig
                kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True)
                print("  🔒 Mode BitsAndBytes INT4 (4-bit) activé.")
            except Exception as e:
                print(f"  ⚠️ BitsAndBytes non disponible ({e}). Repli sur FP16 (16-bit).")

        # Tentative d'import direct d'AutoProcessor ou fallback pipeline
        try:
            from transformers import AutoProcessor, AutoModelForCausalLM
            processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(MODEL_ID, trust_remote_code=True, **kwargs)
            use_pipeline = False
        except (ImportError, AttributeError):
            print("  ⚠️ 'AutoProcessor' non présent dans cette version de transformers.")
            print("  🔄 Tentative avec le pipeline 'image-text-to-text'...")
            from transformers import pipeline
            pipe = pipeline("image-text-to-text", model=MODEL_ID, trust_remote_code=True, model_kwargs=kwargs)
            use_pipeline = True
        
        load_duration = time.time() - t0_load
        print(f"  ✅ Modèle chargé en {load_duration:.2f}s !")
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement du modèle : {e}")
        print("💡 Conseil : Exécutez sur la Jetson :  pip3 install --upgrade transformers accelerate bitsandbytes")
        sys.exit(1)

    # 3. Inférence & Extraction Bounding Box
    print(f"\n🔍 [3/3] Inférence avec le prompt : '{args.prompt}'...")
    t0_infer = time.time()

    try:
        if use_pipeline:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": pil_image},
                        {"type": "text", "text": f"Locate {args.prompt} in this image."}
                    ]
                }
            ]
            outputs = pipe(text=messages)
            result_text = str(outputs)
        else:
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
