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

    # 1. Correctif Syntaxe Python 3.10 (PEP 646 unpacking issue)
    target_syntax = "shifted_indices = shifted_indices[..., *[None for _ in range(len(self.dim_shape))]]"
    replacement_syntax = "shifted_indices = shifted_indices[(Ellipsis,) + (None,) * len(self.dim_shape)]"

    patched = False

    if target_syntax in content:
        print("🛠️  Cible syntaxe trouvée. Remplacement par la syntaxe compatible Python 3.10...")
        content = content.replace(target_syntax, replacement_syntax)
        patched = True
    elif replacement_syntax in content:
        print("ℹ️ Le correctif de syntaxe est déjà appliqué.")
    else:
        print("⚠ Attention : Impossible de trouver le bloc de syntaxe Python 3.11 à corriger (peut-être déjà modifié ?)")

    # 2. Correctif prompt -> prompt_indices (Incompatibilité API pour les modèles avec prompt)
    target_prompt = """            prompt_tensor = torch.zeros(
                [feat_signal.size(0), hidden_length, num_prompts], dtype=feat_signal.dtype, device=device
            )

            # Set the target language
            for i in range(prompt_tensor.size(0)):
                prompt_tensor[i, :, prompt_idx] = 1

        # Call model forward with or without prompt
        if prompt_tensor is not None:
            encoded, encoded_len = self.asr_model.forward(
                processed_signal=feat_signal,
                processed_signal_length=feat_signal_len,
                prompt=prompt_tensor,
            )"""

    replacement_prompt = """            prompt_indices_list = [prompt_idx for _ in range(feat_signal.size(0))]
            prompt_indices_tensor = torch.tensor(prompt_indices_list, dtype=torch.long, device=device)
        else:
            prompt_indices_tensor = None

        # Call model forward with or without prompt
        if prompt_indices_tensor is not None:
            encoded, encoded_len = self.asr_model.forward(
                processed_signal=feat_signal,
                processed_signal_length=feat_signal_len,
                prompt_indices=prompt_indices_tensor,
            )"""

    if target_prompt in content:
        print("🛠️  Cible de prompt trouvée. Remplacement de 'prompt' par 'prompt_indices'...")
        content = content.replace(target_prompt, replacement_prompt)
        patched = True
    elif replacement_prompt in content:
        print("ℹ️ Le correctif du paramètre prompt_indices est déjà appliqué.")
    else:
        # Tentative avec des retours à la ligne normalisés (pour éviter les soucis de CRLF / LF)
        target_prompt_lf = target_prompt.replace('\r\n', '\n')
        content_lf = content.replace('\r\n', '\n')
        if target_prompt_lf in content_lf:
            print("🛠️  Cible de prompt trouvée (avec normalisation LF). Remplacement...")
            content_lf = content_lf.replace(target_prompt_lf, replacement_prompt.replace('\r\n', '\n'))
            content = content_lf
            patched = True
        else:
            print("⚠ Attention : Impossible de trouver le bloc de code prompt/prompt_indices dans le fichier.")

    if patched:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Modifications appliquées avec succès !")
    else:
        print("ℹ️ Aucun changement requis ou tous les correctifs sont déjà en place.")

if __name__ == "__main__":
    main()
