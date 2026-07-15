import os
import sys

def main():
    filepath = os.path.expanduser("~/.local/lib/python3.10/site-packages/nemo/collections/asr/parts/utils/streaming_utils.py")
    if not os.path.exists(filepath):
        print(f"❌ Fichier introuvable : {filepath}")
        print("Veuillez vérifier que nemo_toolkit est bien installé dans le dossier utilisateur.")
        sys.exit(1)

    print(f"📖 Lecture de {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    target = "shifted_indices = shifted_indices[..., *[None for _ in range(len(self.dim_shape))]]"
    replacement = "shifted_indices = shifted_indices[(Ellipsis,) + (None,) * len(self.dim_shape)]"

    if target in content:
        print("🛠️  Cible trouvée. Remplacement de la syntaxe Python 3.11 par une syntaxe compatible Python 3.10...")
        new_content = content.replace(target, replacement)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Correctif appliqué avec succès !")
    elif replacement in content:
        print("ℹ️ Le correctif est déjà appliqué dans le fichier.")
    else:
        print("❌ Impossible de trouver la ligne cible dans le fichier. Il a peut-être déjà été modifié ou a une structure différente.")
        sys.exit(1)

if __name__ == "__main__":
    main()
