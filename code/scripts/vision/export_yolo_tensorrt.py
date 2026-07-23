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

    # Chargement du dictionnaire complet fr_en_dictionary.json
    dict_path = os.path.join(VISION_DIR, "fr_en_dictionary.json")
    all_prompts_en = []
    if os.path.exists(dict_path):
        import json
        try:
            with open(dict_path, 'r', encoding='utf-8') as f:
                fr_dict = json.load(f)
            for fr_word, en_raw in fr_dict.items():
                if fr_word.startswith('_'):
                    continue
                for sub in str(en_raw).split(','):
                    sub_clean = sub.strip()
                    if sub_clean and sub_clean not in all_prompts_en:
                        all_prompts_en.append(sub_clean)
            print(f"📚 [Dictionary] {len(all_prompts_en)} prompts CLIP pré-injectés depuis fr_en_dictionary.json.")
            model.set_classes(all_prompts_en)
        except Exception as e:
            print(f"⚠ Erreur chargement dictionnaire fr_en_dictionary.json : {e}")

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

        # Réinitialisation de la liste des mots en attente après compilation réussie
        if os.path.exists(dict_path):
            try:
                with open(dict_path, 'r', encoding='utf-8') as f:
                    updated_dict = json.load(f)
                updated_dict["_new_words_since_export"] = []
                with open(dict_path, 'w', encoding='utf-8') as f:
                    json.dump(updated_dict, f, ensure_ascii=False, indent=2)
                print("✨ [Notifier] Liste d'attente des nouveaux mots réinitialisée !")
            except Exception as e:
                print(f"⚠ Impossible de réinitialiser la liste d'attente : {e}")
    except Exception as e:
        print(f"❌ Échec de l'exportation : {e}")

if __name__ == "__main__":
    target_model = sys.argv[1] if len(sys.argv) > 1 else "yolov8m-worldv2.pt"
    export_tensorrt(target_model)
