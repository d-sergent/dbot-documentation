#!/opt/homebrew/bin/python3.11
"""Verification du compte API 1min.ai (liste /openai/v1/models a 0 credit + test optionnel)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

_RAG_DIR = str(Path(__file__).resolve().parent)
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

from rag_runtime import (  # noqa: E402
    DEFAULT_ONEMINAI_MODEL,
    ONEMINAI_RECOMMENDED_MODELS,
    adapt_1minai_payload_from_error,
    build_1minai_chat_payload,
    fetch_1minai_models,
    resolve_1minai_config,
)

_REPO_ENV = Path(__file__).resolve().parent.parent.parent / ".env"
if _REPO_ENV.exists():
    load_dotenv(dotenv_path=_REPO_ENV)
else:
    load_dotenv()


def check_1minai(test_model: str | None = None) -> int:
    base_url, default_model, api_key = resolve_1minai_config()
    if not api_key or "<VOTRE_CLE" in api_key:
        print("❌ ONEMINAI_API_KEY manquante dans .env")
        return 1

    print(f"🔑 Cle 1min.ai detectee (...{api_key[-4:]}) | Endpoint : {base_url}")
    print(f"🎯 Modele par defaut configure : {default_model}")

    try:
        models = fetch_1minai_models(base_url=base_url, api_key=api_key, timeout=15.0)
    except Exception as exc:
        print(f"❌ Impossible de lister /models sur 1min.ai : {exc}")
        return 1

    print(f"\n--- Modeles recommandes pour LightRAG D-Bot ({len(models)} modeles totaux) ---")
    model_set = set(models)
    for cand in ONEMINAI_RECOMMENDED_MODELS:
        status = "✅ Disponible" if cand in model_set else "ℹ️ Non liste (verifier casse/alias)"
        print(f"  - {cand:30s} : {status}")

    if models:
        sample_others = [m for m in models if m not in ONEMINAI_RECOMMENDED_MODELS]
        if sample_others:
            print(f"\nAutres modeles disponibles ({len(sample_others)}) :")
            for m in sample_others:
                print(f"  * {m}")

    if test_model:
        target = default_model if test_model == "default" else test_model
        print(f"\n--- Test unitaire minimal ({target}) ---")
        payload = build_1minai_chat_payload(
            target,
            [{"role": "user", "content": "Reponds uniquement par OK."}],
            temperature=0.1,
            max_tokens=16,
            stream=False,
        )
        if "temperature" not in payload:
            print(f"ℹ️ Contrainte modele ({target}) : parametre temperature omis automatiquement.")
        try:
            resp = None
            for _ in range(4):
                resp = requests.post(
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30.0,
                )
                if resp.status_code == 200:
                    break
                if resp.status_code == 400:
                    adapted = adapt_1minai_payload_from_error(target, payload, resp.text)
                    if adapted is not None:
                        payload, change_desc = adapted
                        print(f"⚙️ Adaptation parametre ({target}) : {change_desc} -> nouvel essai...")
                        continue
                break
            if resp is None or resp.status_code != 200:
                code = resp.status_code if resp is not None else "?"
                body = resp.text[:500] if resp is not None else "aucune reponse"
                print(f"❌ HTTP {code} : {body}")
                return 1
            data = resp.json()
            txt = ((data.get("choices") or [{}])[0].get("message") or {}).get("content", "").strip()
            usage = data.get("usage") or {}
            print(f"🤖 Reponse : {json.dumps(txt, ensure_ascii=False)}")
            print(
                f"📊 Usage : prompt={usage.get('prompt_tokens', '?')} tok | "
                f"completion={usage.get('completion_tokens', '?')} tok | "
                f"total={usage.get('total_tokens', '?')} tok"
            )
        except Exception as exc:
            print(f"❌ Erreur requete test ({target}) : {exc}")
            return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Liste les modeles 1min.ai actifs sur votre cle (0 credit) et teste optionnellement un modele."
    )
    parser.add_argument(
        "--test-model",
        type=str,
        default=None,
        help=f"Envoyer un mini ping 'Reponds OK.' a un modele precis (ex: {DEFAULT_ONEMINAI_MODEL} ou 'default').",
    )
    args = parser.parse_args()
    return check_1minai(test_model=args.test_model)


if __name__ == "__main__":
    raise SystemExit(main())
