#!/opt/homebrew/bin/python3.11
"""
Tests unitaires isoles (offline, sans ecrire dans lightrag_dbot_db ni lancer index_docs.py)
couvrant les 4 volets de resilience du RAG D-Bot et le cycle de vie Ollama.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_RAG_DIR = str(Path(__file__).resolve().parent)
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

import ask_rag  # noqa: E402
import index_docs  # noqa: E402
import rag_runtime  # noqa: E402


class _MockHTTPResponse:
    def __init__(self, status_code: int, payload: dict | None = None) -> None:
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload


class TestRagResilience(unittest.IsolatedAsyncioTestCase):
    def test_unsloth_env_precedence_and_legacy_fallback(self) -> None:
        clean_env = {
            k: v
            for k, v in os.environ.items()
            if not k.startswith(("UNSLOTH_", "VMLX_"))
        }
        with patch.dict(os.environ, clean_env, clear=True):
            self.assertEqual(
                rag_runtime.resolve_unsloth_config(),
                ("http://127.0.0.1:8888/v1", "unsloth/Qwen3.8-27B-GGUF", "EMPTY"),
            )

        with patch.dict(
            os.environ,
            {
                **clean_env,
                "VMLX_BASE_URL": "http://127.0.0.1:9999/v1/",
                "VMLX_MODEL": "legacy-model",
                "VMLX_API_KEY": "legacy-tok",
            },
            clear=True,
        ):
            self.assertEqual(
                rag_runtime.resolve_unsloth_config(),
                ("http://127.0.0.1:9999/v1", "legacy-model", "legacy-tok"),
            )

        with patch.dict(
            os.environ,
            {
                **clean_env,
                "VMLX_BASE_URL": "http://127.0.0.1:9999/v1",
                "UNSLOTH_BASE_URL": "http://127.0.0.1:8888/v1/",
                "UNSLOTH_MODEL": "unsloth/Qwen3.8-27B-GGUF",
                "UNSLOTH_API_KEY": "unsloth-tok",
            },
            clear=True,
        ):
            self.assertEqual(
                rag_runtime.resolve_unsloth_config(),
                ("http://127.0.0.1:8888/v1", "unsloth/Qwen3.8-27B-GGUF", "unsloth-tok"),
            )

    async def test_index_docs_local_defaults_aligned_to_unsloth(self) -> None:
        clean_env = {
            k: v
            for k, v in os.environ.items()
            if not k.startswith(("UNSLOTH_", "VMLX_"))
        }
        captured: list[dict] = []

        async def _fake_openai_complete(model, prompt, **kwargs):
            captured.append({"model": model, **kwargs})
            return "ok"

        with patch.dict(os.environ, clean_env, clear=True), patch.object(
            index_docs, "openai_complete_if_cache", side_effect=_fake_openai_complete
        ):
            for prov in ("local", "unsloth"):
                args = argparse.Namespace(provider=prov, model=None, api_key=None)
                fn = await index_docs.get_llm_func(args)
                self.assertTrue(callable(fn))
                await fn("ping")

        self.assertEqual(len(captured), 2)
        for call in captured:
            self.assertEqual(call["base_url"], "http://127.0.0.1:8888/v1")
            self.assertEqual(call["model"], "unsloth/Qwen3.8-27B-GGUF")

    def test_extract_lexical_keywords_preserves_technical_ids(self) -> None:
        hl, ll = rag_runtime.extract_lexical_keywords(
            "Quel jeu pour le roulement RB8016 et le moteur RS-06 sur PA12-CF ?"
        )
        self.assertTrue(hl)
        self.assertTrue(ll)
        joined_ll = " ".join(ll)
        self.assertIn("RB8016", joined_ll)
        self.assertIn("RS-06", joined_ll)
        self.assertIn("PA12-CF", joined_ll)
        self.assertNotIn("Quel", ll)
        self.assertNotIn("pour", ll)

    def test_filter_and_clean_chunks_keeps_svg_and_pdf(self) -> None:
        chunks = [
            {"file_path": "img/view.png", "content": "image", "rerank_score": 0.99},
            {"file_path": "diagrams/waist.svg", "content": "svg schema", "rerank_score": 0.45},
            {"file_path": "specs/datasheet.pdf", "content": "pdf doc", "rerank_score": 0.85},
            {"file_path": "docs/guide.md", "content": "markdown doc", "rerank_score": 0.70},
        ]
        filtered = rag_runtime.filter_and_clean_chunks(chunks, skip_images=True)
        paths = [c["file_path"] for c in filtered]
        self.assertEqual(paths, ["specs/datasheet.pdf", "docs/guide.md", "diagrams/waist.svg"])

        all_kept = rag_runtime.filter_and_clean_chunks(chunks, skip_images=False)
        self.assertEqual(len(all_kept), 4)
        self.assertEqual(all_kept[0]["file_path"], "img/view.png")

    def test_resolve_active_provider_cascade_and_model_check(self) -> None:
        def _mock_get(url, **kwargs):
            if url.endswith("/api/tags"):
                return _MockHTTPResponse(200, {"models": [{"name": "qwen3.5:9b"}]})
            if url.endswith("/models"):
                return _MockHTTPResponse(200, {"data": [{"id": "unsloth/Qwen3.8-27B-GGUF"}]})
            return _MockHTTPResponse(404)

        with patch.object(rag_runtime.requests, "get", side_effect=_mock_get):
            # Ollama ne possede pas qwen3.8:27b-mlx -> cascade vers unsloth
            chosen = rag_runtime.resolve_active_provider(
                "auto",
                ollama_model="qwen3.8:27b-mlx",
                gemini_key="placeholder-gemini",
                openrouter_key="placeholder-or",
            )
            self.assertEqual(chosen, "unsloth")

        def _mock_get_with_mlx(url, **kwargs):
            if url.endswith("/api/tags"):
                return _MockHTTPResponse(200, {"models": [{"name": "qwen3.8:27b-mlx"}]})
            return _MockHTTPResponse(500)

        with patch.object(rag_runtime.requests, "get", side_effect=_mock_get_with_mlx):
            self.assertEqual(
                rag_runtime.resolve_active_provider("auto", ollama_model="qwen3.8:27b-mlx"),
                "ollama",
            )

    def test_managed_ollama_never_kills_external_daemon(self) -> None:
        server = rag_runtime.ManagedOllamaServer(base_url="http://127.0.0.1:11434", model="qwen3.8:27b-mlx")
        with patch.object(rag_runtime, "check_ollama_ready", return_value=True), patch.object(
            rag_runtime.subprocess, "Popen"
        ) as mock_popen, patch.object(rag_runtime.requests, "post") as mock_post:
            self.assertTrue(server.ensure_started())
            self.assertFalse(server.started_by_us)
            mock_popen.assert_not_called()
            server.cleanup()
            mock_post.assert_not_called()

    def test_managed_ollama_starts_and_cleans_up_owned_process(self) -> None:
        server = rag_runtime.ManagedOllamaServer(base_url="http://127.0.0.1:11434", model="qwen3.8:27b-mlx")
        fake_proc = MagicMock()
        fake_proc.poll.return_value = None

        ready_states = iter([False, True, True])
        with patch.object(rag_runtime, "check_ollama_ready", side_effect=lambda *a, **k: next(ready_states, True)), patch.object(
            rag_runtime, "_find_ollama_binary", return_value="/usr/local/bin/ollama"
        ), patch.object(rag_runtime.subprocess, "Popen", return_value=fake_proc) as mock_popen, patch.object(
            rag_runtime.requests, "post", return_value=_MockHTTPResponse(200)
        ) as mock_post:
            self.assertTrue(server.ensure_started(timeout_s=2.0))
            self.assertTrue(server.started_by_us)
            kwargs = mock_popen.call_args.kwargs
            self.assertFalse(kwargs["shell"])
            self.assertEqual(kwargs["env"]["OLLAMA_NUM_PARALLEL"], "1")
            self.assertEqual(kwargs["env"]["OLLAMA_MAX_LOADED_MODELS"], "1")
            self.assertEqual(kwargs["env"]["OLLAMA_FLASH_ATTENTION"], "1")

            server.cleanup()
            mock_post.assert_called_once()
            fake_proc.terminate.assert_called_once()
            self.assertFalse(server.started_by_us)

    def test_ask_rag_default_provider_is_auto(self) -> None:
        parsed = ask_rag.build_arg_parser().parse_args(["architecture waist"])
        self.assertEqual(parsed.provider, "auto")

    async def test_ask_rag_search_only_hybrid_fallback_without_llm(self) -> None:
        calls: list[dict] = []

        class _FakeLightRAG:
            def __init__(self, *args, **kwargs) -> None:
                pass

            async def initialize_storages(self) -> None:
                return None

            async def aquery_data(self, query: str, param) -> dict:
                calls.append(
                    {
                        "mode": param.mode,
                        "hl": list(param.hl_keywords or []),
                        "ll": list(param.ll_keywords or []),
                    }
                )
                if param.mode == "hybrid":
                    raise RuntimeError("Simulated graph error")
                return {
                    "data": {
                        "chunks": [
                            {
                                "file_path": "01_Mecanique_et_Chassis/test_waist.md",
                                "content": "Butee mecanique bassin RB8016.",
                                "rerank_score": 0.91,
                            }
                        ],
                        "entities": [],
                        "relationships": [],
                    }
                }

        with tempfile.TemporaryDirectory() as tmp_dir, patch.object(ask_rag, "DB_PATH", tmp_dir), patch.object(
            ask_rag, "LightRAG", _FakeLightRAG
        ), patch.object(ask_rag, "get_rerank_model", return_value=None):
            args = ask_rag.build_arg_parser().parse_args(
                ["--search-only", "--mode", "hybrid", "butee mecanique RB8016"]
            )
            code = await ask_rag.run_cli(args)

        self.assertEqual(code, 0)
        self.assertEqual(calls[0]["mode"], "hybrid")
        self.assertTrue(calls[0]["hl"])
        self.assertIn("RB8016", calls[0]["ll"])
        self.assertEqual(calls[1]["mode"], "naive")

    async def test_ask_rag_search_only_hybrid_succeeds_without_spawning_llm(self) -> None:
        calls: list[dict] = []

        class _FakeLightRAGHybridOK:
            def __init__(self, *args, **kwargs) -> None:
                self.llm_model_func = kwargs["llm_model_func"]

            async def initialize_storages(self) -> None:
                return None

            async def aquery_data(self, query: str, param) -> dict:
                calls.append({"mode": param.mode, "hl": param.hl_keywords, "ll": param.ll_keywords})
                return {
                    "data": {
                        "chunks": [
                            {
                                "file_path": "01_Mecanique_et_Chassis/DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md",
                                "content": "Roulement RB8016 et moteur RS-06.",
                                "rerank_score": 0.96,
                            }
                        ],
                        "entities": [{"entity_name": "RB8016", "description": "Roulement a rouleaux croises"}],
                        "relationships": [{"src_id": "RB8016", "tgt_id": "RS-06", "description": "Entrainement waist"}],
                    }
                }

        with tempfile.TemporaryDirectory() as tmp_dir, patch.object(ask_rag, "DB_PATH", tmp_dir), patch.object(
            ask_rag, "LightRAG", _FakeLightRAGHybridOK
        ), patch.object(ask_rag, "ManagedOllamaServer") as mock_srv, patch.object(
            ask_rag, "get_rerank_model", return_value=None
        ):
            args = ask_rag.build_arg_parser().parse_args(
                ["--search-only", "--mode", "hybrid", "--keywords", "waist,RB8016", "architecture waist RB8016"]
            )
            code = await ask_rag.run_cli(args)

        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["mode"], "hybrid")
        self.assertEqual(calls[0]["ll"], ["waist", "RB8016"])
        mock_srv.return_value.ensure_started.assert_not_called()

    async def test_ask_rag_synthesis_autostarts_and_cleans_up_ollama(self) -> None:
        class _FakeLightRAGSynth:
            def __init__(self, *args, **kwargs) -> None:
                pass

            async def initialize_storages(self) -> None:
                return None

            async def aquery(self, query: str, param) -> str:
                return "Reponse synthetisee de test."

        lifecycle_events: list[str] = []

        class _FakeManagedOllama:
            def __init__(self, base_url=None, model=None) -> None:
                self.started_by_us = False

            def ensure_started(self, timeout_s: float = 15.0) -> bool:
                lifecycle_events.append("start")
                self.started_by_us = True
                return True

            def cleanup(self, force_unload_external: bool = False) -> None:
                lifecycle_events.append(f"cleanup:{force_unload_external}")
                self.started_by_us = False

        check_calls = iter([False, True])
        with tempfile.TemporaryDirectory() as tmp_dir, patch.object(ask_rag, "DB_PATH", tmp_dir), patch.object(
            ask_rag, "LightRAG", _FakeLightRAGSynth
        ), patch.object(ask_rag, "ManagedOllamaServer", _FakeManagedOllama), patch.object(
            ask_rag, "check_ollama_ready", side_effect=lambda *a, **k: next(check_calls, True)
        ), patch.object(ask_rag, "get_rerank_model", return_value=None):
            args = ask_rag.build_arg_parser().parse_args(
                ["--provider", "ollama", "architecture waist"]
            )
            code = await ask_rag.run_cli(args)

        self.assertEqual(code, 0)
        self.assertEqual(lifecycle_events, ["start", "cleanup:False"])


if __name__ == "__main__":
    unittest.main()
