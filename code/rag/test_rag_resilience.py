#!/opt/homebrew/bin/python3.11
"""
Tests unitaires isoles (offline, sans ecrire dans lightrag_dbot_db ni lancer index_docs.py)
couvrant les 4 volets de resilience du RAG D-Bot et le cycle de vie Ollama.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

_RAG_DIR = str(Path(__file__).resolve().parent)
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

import ask_rag  # noqa: E402
import check_1minai  # noqa: E402
import index_docs  # noqa: E402
import rag_runtime  # noqa: E402


class _MockHTTPResponse:
    def __init__(self, status_code: int, payload: dict | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

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
            # En mode auto (online-first par defaut), Gemini est prioritaire si une cle est presente
            chosen_online = rag_runtime.resolve_active_provider(
                "auto",
                ollama_model="qwen3.8:27b-mlx",
                gemini_key="placeholder-gemini",
                openrouter_key="placeholder-or",
                oneminai_key="",
            )
            self.assertEqual(chosen_online, "gemini")

            # Sans Gemini, qa/audit utilisent 1minai si une cle 1min.ai est configuree
            chosen_1min = rag_runtime.resolve_active_provider(
                "auto",
                ollama_model="gemma4:26b",
                gemini_key="",
                openrouter_key="placeholder-or",
                role="audit",
                oneminai_key="placeholder-1min",
            )
            self.assertEqual(chosen_1min, "1minai")

            # Hors ligne (sans Gemini ni 1minai), Ollama ne possede pas gemma4:26b -> cascade vers unsloth
            chosen_offline = rag_runtime.resolve_active_provider(
                "auto",
                ollama_model="gemma4:26b",
                gemini_key="",
                openrouter_key="placeholder-or",
                role="audit",
                oneminai_key="",
            )
            self.assertEqual(chosen_offline, "unsloth")

        def _mock_get_with_mlx(url, **kwargs):
            if url.endswith("/api/tags"):
                return _MockHTTPResponse(200, {"models": [{"name": "qwen3.8:27b-mlx"}, {"name": "gemma4:26b"}]})
            return _MockHTTPResponse(500)

        with patch.object(rag_runtime.requests, "get", side_effect=_mock_get_with_mlx):
            self.assertEqual(
                rag_runtime.resolve_active_provider(
                    "auto", ollama_model="gemma4:26b", gemini_key="", oneminai_key=""
                ),
                "ollama",
            )

        with patch.dict(os.environ, {"OLLAMA_MODEL": "qwen3.8:27b-mlx"}, clear=False):
            os.environ.pop("OLLAMA_QA_MODEL", None)
            os.environ.pop("OLLAMA_AUDIT_MODEL", None)
            self.assertEqual(rag_runtime.resolve_ollama_config("index")[1], "qwen3.8:27b-mlx")
            self.assertEqual(rag_runtime.resolve_ollama_config("qa")[1], "gemma4:26b")
            self.assertEqual(rag_runtime.resolve_ollama_config("audit")[1], "gemma4:26b")

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

    async def test_index_docs_ollama_translates_aiohttp_client_error_to_runtime_error(self) -> None:
        import aiohttp

        llm_ollama = index_docs._build_ollama_llm_func("gemma4:26b")
        with patch.object(
            index_docs.aiohttp.ClientSession,
            "post",
            side_effect=aiohttp.ClientConnectorError(MagicMock(), OSError(61, "Connection refused")),
        ):
            with self.assertRaises(RuntimeError) as ctx:
                await llm_ollama("ping")
        self.assertIn("Ollama injoignable", str(ctx.exception))

    async def test_index_docs_ollama_autostarts_and_cleans_up_managed_server(self) -> None:
        lifecycle_events: list[str] = []

        class _FakeManagedOllama:
            def __init__(self, base_url=None, model=None) -> None:
                self.base_url = base_url or "http://127.0.0.1:11434"
                self.model = model or "gemma4:26b"
                self.started_by_us = False

            def ensure_started(self, timeout_s: float = 15.0) -> bool:
                lifecycle_events.append(f"start:{self.model}")
                self.started_by_us = True
                return True

            def cleanup(self, force_unload_external: bool = False) -> None:
                lifecycle_events.append(f"cleanup:{force_unload_external}")
                self.started_by_us = False

        class _FakeDocStatus:
            _storage_lock = index_docs.asyncio.Lock()
            _data = {}

            async def get_by_id(self, doc_id: str) -> dict:
                return {"status": "processed", "file_path": "sample.md"}

        class _FakeLightRAGIndex:
            def __init__(self, *args, **kwargs) -> None:
                self.doc_status = _FakeDocStatus()
                self.full_docs = None

            async def initialize_storages(self) -> None:
                return None

            async def ainsert(self, content: str, ids=None, file_paths=None) -> None:
                lifecycle_events.append(f"insert:{file_paths}")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            doc_file = tmp_path / "sample.md"
            doc_file.write_text("# Sample", encoding="utf-8")
            db_dir = tmp_path / "db"
            args = index_docs.parse_cli_args(["--provider", "ollama", "--model", "gemma4:26b", "--files", str(doc_file)])
            with patch.object(index_docs, "DB_PATH", db_dir), patch.object(
                index_docs, "INDEX_LOG", db_dir / "indexed_files.json"
            ), patch.object(index_docs, "ManagedOllamaServer", _FakeManagedOllama), patch.object(
                index_docs, "_check_ollama_ready", return_value=(True, "OK")
            ), patch.object(index_docs, "LightRAG", _FakeLightRAGIndex):
                await index_docs.run_indexing(args)

        self.assertEqual(lifecycle_events[0], "start:gemma4:26b")
        self.assertTrue(any(ev.startswith("insert:") for ev in lifecycle_events))
        self.assertEqual(lifecycle_events[-1], "cleanup:False")

    async def test_index_docs_ollama_aborts_before_insert_when_model_missing(self) -> None:
        lifecycle_events: list[str] = []

        class _FakeManagedOllama:
            def __init__(self, base_url=None, model=None) -> None:
                self.base_url = base_url or "http://127.0.0.1:11434"
                self.model = model or "missing:model"

            def ensure_started(self, timeout_s: float = 15.0) -> bool:
                lifecycle_events.append("start")
                return True

            def cleanup(self, force_unload_external: bool = False) -> None:
                lifecycle_events.append("cleanup")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            doc_file = tmp_path / "sample.md"
            doc_file.write_text("# Sample", encoding="utf-8")
            args = index_docs.parse_cli_args(["--provider", "ollama", "--model", "missing:model", "--files", str(doc_file)])
            with patch.object(index_docs, "DB_PATH", tmp_path / "db"), patch.object(
                index_docs, "ManagedOllamaServer", _FakeManagedOllama
            ), patch.object(
                index_docs, "_check_ollama_ready", return_value=(False, "modèle 'missing:model' absent")
            ), patch.object(index_docs, "LightRAG") as mock_rag:
                await index_docs.run_indexing(args)
                mock_rag.assert_not_called()

        self.assertEqual(lifecycle_events, ["start", "cleanup"])

    async def test_index_docs_auto_lazy_starts_ollama_only_on_fallback(self) -> None:
        started: list[str] = []

        class _FakeManagedOllama:
            def __init__(self, base_url=None, model=None) -> None:
                self.base_url = base_url or "http://127.0.0.1:11434"
                self.model = model or "qwen3.8:27b-mlx"

            def ensure_started(self, timeout_s: float = 15.0) -> bool:
                started.append(self.model)
                return True

        managed = _FakeManagedOllama(model="gemma4:26b")
        args = index_docs.parse_cli_args(["--provider", "auto", "--model", "gemma4:26b"])
        with patch.dict(os.environ, {"ONEMINAI_API_KEY": ""}, clear=False):
            state = index_docs._create_auto_state(args, api_key="dummy-key", managed_ollama=managed)
            with patch.object(index_docs, "_create_genai_client", return_value=object()), patch.object(
                index_docs, "_check_ollama_ready", side_effect=[(False, "stopped"), (True, "OK")]
            ), patch.object(
                index_docs, "_call_gemini_cascade", return_value=(None, None)
            ), patch.object(
                index_docs, "_post_json_aiohttp", return_value={"message": {"content": "ok-fallback"}}
            ) as mock_post:
                state["cloud_exhausted"] = True
                fn = await index_docs.get_llm_func(args, auto_state=state, managed_ollama=managed)
                self.assertEqual(started, [])
                res = await fn("ping")

        self.assertEqual(res, "ok-fallback")
        self.assertEqual(started, ["gemma4:26b"])
        self.assertTrue(state["ollama_verified"])
        mock_post.assert_awaited_once()

    def test_get_gemini_timeout_enforces_minimum_10s(self) -> None:
        with patch.dict(os.environ, {"GEMINI_HTTP_TIMEOUT_S": "5", "GEMINI_QA_TIMEOUT_S": "3"}, clear=False):
            self.assertEqual(rag_runtime.get_gemini_timeout_s("index"), 10.0)
            self.assertEqual(rag_runtime.get_gemini_timeout_s("qa"), 10.0)

    async def test_gemini_cascade_retries_without_thinking_on_400_and_tracks_model(self) -> None:
        calls: list[tuple[str, bool]] = []

        class _FakeModels:
            def generate_content(self, *, model, contents, config):
                has_thinking = getattr(config, "thinking_config", None) is not None
                calls.append((model, has_thinking))
                if model == "gemini-3.8-flash":
                    raise RuntimeError("503 UNAVAILABLE. high demand")
                if model == "gemini-3.5-flash-lite" and has_thinking:
                    raise RuntimeError("400 INVALID_ARGUMENT. thinking_budget unsupported")
                return MagicMock(text="reponse validée")

        fake_client = MagicMock(models=_FakeModels())
        tracker = rag_runtime.ModelExecutionTracker(role="qa")
        sess = rag_runtime.GeminiCascadeSession(
            ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"],
            timeout_s=15.0,
            thinking_budget=0,
            wait_on_transient=False,
            tracker=tracker,
        )
        text, used_model = await sess.call(fake_client, "question test", tracker=tracker)
        self.assertEqual(text, "reponse validée")
        self.assertEqual(used_model, "gemini-3.5-flash-lite")
        self.assertIn("gemini-3.5-flash-lite", sess.no_thinking_models)
        self.assertEqual(
            calls,
            [
                ("gemini-3.8-flash", True),
                ("gemini-3.5-flash-lite", True),
                ("gemini-3.5-flash-lite", False),
            ],
        )
        summary = tracker.format_summary()
        self.assertIn("gemini / gemini-3.5-flash-lite", summary)
        self.assertIn("gemini-3.8-flash->503 UNAVAILABLE", summary)

    def test_build_gemini_cascade_excludes_lite_for_index_keeps_for_qa(self) -> None:
        clean_env = {k: v for k, v in os.environ.items() if k not in ("GEMINI_AUTO_MODELS", "RAG_DEFAULT_MODEL")}
        with patch.dict(os.environ, clean_env, clear=True):
            idx_cascade = rag_runtime.build_gemini_cascade("index")
            qa_cascade = rag_runtime.build_gemini_cascade("qa")
            audit_cascade = rag_runtime.build_gemini_cascade("audit")

        self.assertEqual(len(idx_cascade), 8)
        self.assertTrue(all("lite" not in model.lower() for model in idx_cascade), idx_cascade)
        self.assertIn("gemini-3.8-flash", idx_cascade)
        self.assertIn("gemini-2.5-flash", idx_cascade)

        expected_fast_lite = ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-flash-lite-latest"]
        self.assertEqual(qa_cascade, expected_fast_lite)
        self.assertEqual(audit_cascade, expected_fast_lite)
        self.assertTrue(all("lite" in m.lower() for m in qa_cascade), qa_cascade)

        explicit_override = rag_runtime.build_gemini_cascade("index", explicit_model="gemini-3.5-flash-lite")
        self.assertEqual(explicit_override[0], "gemini-3.5-flash-lite")

    async def test_ask_rag_auto_prefers_gemini_then_falls_back_to_gemma4_qa(self) -> None:
        tracker = rag_runtime.ModelExecutionTracker(role="qa")
        posted_models: list[str] = []

        class _FakePostResp:
            status = 200

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def json(self):
                return {"message": {"content": "Reponse rapide Gemma 4"}}

        def _fake_post(url, json=None, **kwargs):
            posted_models.append((json or {}).get("model"))
            return _FakePostResp()

        managed = MagicMock()
        managed.ensure_started.return_value = True

        async def _fake_fail_gemini(*args, **kwargs):
            tracker.record_failure("gemini", "gemini-3.8-flash", "503 UNAVAILABLE")
            return None, None

        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key", "ONEMINAI_API_KEY": ""}, clear=False), patch.object(
            ask_rag, "create_genai_client", return_value=object()
        ), patch.object(
            rag_runtime.GeminiCascadeSession, "call", side_effect=_fake_fail_gemini
        ), patch.object(
            ask_rag, "check_ollama_ready", side_effect=lambda url, required_model=None, timeout=0.5: required_model in (None, "gemma4:26b")
        ), patch.object(
            ask_rag.aiohttp.ClientSession, "post", side_effect=_fake_post
        ):
            fn = ask_rag._build_auto_qa_llm_func(
                model_override=None,
                api_key_override=None,
                managed_ollama=managed,
                auto_start_allowed=True,
                tracker=tracker,
            )
            answer = await fn("Quel est le jeu RB8016 ?")

        self.assertEqual(answer, "Reponse rapide Gemma 4")
        self.assertEqual(posted_models, ["gemma4:26b"])
        self.assertIn("ollama / gemma4:26b", tracker.format_summary())
        self.assertIn("gemini-3.8-flash->503 UNAVAILABLE", tracker.format_summary())

    async def test_ask_rag_and_check_integrity_auto_3tier_lite_1minai_gemma4(self) -> None:
        import check_integrity  # noqa: E402

        rag_runtime.reset_1minai_model_quirks()
        seen_1minai_qa: list[tuple[str, str]] = []
        seen_ollama_qa: list[str] = []

        class _FakeOllamaResp:
            status = 200

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def json(self):
                return {"message": {"content": "Reponse QA via Ollama Gemma 4"}}

        def _fake_qa_ollama_post(url, json=None, **kwargs):
            seen_ollama_qa.append((json or {}).get("model"))
            return _FakeOllamaResp()

        async def _fake_1minai_qa(model, messages, **kwargs):
            seen_1minai_qa.append((model, str(kwargs.get("api_key"))))
            if len(seen_1minai_qa) == 1:
                return "Reponse QA 1min.ai rapide", 320, 45
            raise RuntimeError('1min.ai HTTP 402: {"error":{"message":"Insufficient credits"}}')

        async def _fake_fail_gemini(*args, **kwargs):
            return None, None

        tracker_qa = rag_runtime.ModelExecutionTracker(role="qa")
        managed_qa = MagicMock()
        managed_qa.ensure_started.return_value = True

        with patch.dict(
            os.environ,
            {"GEMINI_API_KEY": "fake-gem", "ONEMINAI_API_KEY": "fake-1min-qa", "ONEMINAI_QA_MODEL": ""},
            clear=False,
        ), patch.object(
            ask_rag, "create_genai_client", return_value=object()
        ), patch.object(
            rag_runtime.GeminiCascadeSession, "call", side_effect=_fake_fail_gemini
        ), patch.object(
            rag_runtime, "call_1minai_stateless_async", side_effect=_fake_1minai_qa
        ), patch.object(
            ask_rag, "check_ollama_ready", side_effect=lambda url, required_model=None, timeout=0.5: required_model in (None, "gemma4:26b")
        ), patch.object(
            ask_rag.aiohttp.ClientSession, "post", side_effect=_fake_qa_ollama_post
        ):
            fn_qa = ask_rag._build_auto_qa_llm_func(
                model_override=None,
                api_key_override=None,
                managed_ollama=managed_qa,
                auto_start_allowed=True,
                tracker=tracker_qa,
            )
            r1 = await fn_qa("Question 1")
            managed_qa.ensure_started.assert_not_called()
            self.assertEqual(r1, "Reponse QA 1min.ai rapide")
            self.assertEqual(seen_1minai_qa, [("mistral-small-2603", "fake-1min-qa")])

            # Appel 2 : 1min.ai retourne HTTP 402 -> bascule sur Ollama gemma4:26b
            r2 = await fn_qa("Question 2")
            self.assertEqual(r2, "Reponse QA via Ollama Gemma 4")
            self.assertEqual(seen_ollama_qa, ["gemma4:26b"])

        # Meme cascade 3 paliers (Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b) dans check_integrity
        audit_1min_calls: list[str] = []
        audit_ollama_calls: list[str] = []

        async def _fake_1minai_audit(model, messages, **kwargs):
            audit_1min_calls.append(model)
            if len(audit_1min_calls) == 1:
                return "Contradiction RS05.\n\n**Question :** Quelle version RS05 ?", 900, 120
            raise RuntimeError('1min.ai HTTP 402: {"error":{"message":"Quota exceeded"}}')

        async def _fake_ollama_audit(prompt, system_prompt=None, history_messages=None, **kwargs):
            audit_ollama_calls.append(prompt)
            return "Repli Audit Gemma 4"

        tracker_aud = rag_runtime.ModelExecutionTracker(role="audit")
        args_aud = argparse.Namespace(provider="auto", model=None, api_key=None)
        with patch.dict(
            os.environ,
            {"GEMINI_API_KEY": "fake-gem", "ONEMINAI_API_KEY": "fake-1min-aud", "ONEMINAI_AUDIT_MODEL": ""},
            clear=False,
        ), patch.object(
            check_integrity, "create_genai_client", return_value=object()
        ), patch.object(
            rag_runtime.GeminiCascadeSession, "call", side_effect=_fake_fail_gemini
        ), patch.object(
            rag_runtime, "call_1minai_stateless_async", side_effect=_fake_1minai_audit
        ), patch.object(
            check_integrity, "check_ollama_ready", side_effect=lambda url, required_model=None, timeout=0.5: required_model in (None, "gemma4:26b")
        ), patch.object(
            check_integrity, "_build_ollama_audit_llm", return_value=_fake_ollama_audit
        ) as mock_ol_builder:
            fn_aud = await check_integrity.get_llm_func(args_aud, tracker=tracker_aud)
            a1 = await fn_aud("audit section 1")
            self.assertIn("**Question :**", a1)
            self.assertEqual(audit_1min_calls, ["mistral-small-2603"])
            mock_ol_builder.assert_not_called()

            a2 = await fn_aud("audit section 2")
            self.assertEqual(a2, "Repli Audit Gemma 4")
            self.assertEqual(mock_ol_builder.call_args.args[1], "gemma4:26b")

    async def test_ask_rag_auto_honors_explicit_model_for_managed_ollama(self) -> None:
        captured_models: list[str] = []

        class _CaptureManaged:
            def __init__(self, base_url=None, model=None) -> None:
                captured_models.append(model)
                self.started_by_us = False
                self.model = model

            def ensure_started(self, timeout_s: float = 15.0) -> bool:
                return True

            def cleanup(self, force_unload_external: bool = False) -> None:
                return None

        class _FakeLightRAG:
            def __init__(self, *args, **kwargs) -> None:
                pass

            async def initialize_storages(self) -> None:
                return None

            async def aquery(self, query: str, param) -> str:
                return "ok"

        with tempfile.TemporaryDirectory() as tmp_dir, patch.object(ask_rag, "DB_PATH", tmp_dir), patch.object(
            ask_rag, "LightRAG", _FakeLightRAG
        ), patch.object(ask_rag, "ManagedOllamaServer", _CaptureManaged), patch.object(
            ask_rag, "check_ollama_ready", return_value=True
        ), patch.object(ask_rag, "get_rerank_model", return_value=None):
            args = ask_rag.build_arg_parser().parse_args(
                ["--provider", "auto", "--model", "qwen3.8:27b-mlx", "test"]
            )
            code = await ask_rag.run_cli(args)

        self.assertEqual(code, 0)
        self.assertEqual(captured_models, ["qwen3.8:27b-mlx"])

    async def test_check_integrity_ollama_and_unsloth_fixes(self) -> None:
        import check_integrity  # noqa: E402

        captured_unsloth: list[dict] = []

        class _FakeCompletions:
            async def create(self, **kwargs):
                captured_unsloth.append(kwargs)
                return MagicMock(choices=[MagicMock(message=MagicMock(content="ok-unsloth"), finish_reason="stop")])

        fake_openai = MagicMock(chat=MagicMock(completions=_FakeCompletions()))
        args_unsloth = argparse.Namespace(provider="unsloth", model=None, api_key=None)
        with patch.object(check_integrity.openai, "AsyncOpenAI", return_value=fake_openai):
            fn_u = await check_integrity.get_llm_func(args_unsloth)
            out_u = await fn_u("audit")
        self.assertEqual(out_u, "ok-unsloth")
        self.assertEqual(
            captured_unsloth[0]["extra_body"]["chat_template_kwargs"],
            {"enable_thinking": False},
        )

        # Verifie qu'en --provider ollama il n'y a plus de NameError: sys ni crash
        args_ollama = argparse.Namespace(provider="ollama", model=None, api_key=None)
        tracker_ol = rag_runtime.ModelExecutionTracker(role="audit")
        with patch.object(check_integrity, "check_ollama_ready", return_value=True):
            fn_o = await check_integrity.get_llm_func(args_ollama, tracker=tracker_ol)
        self.assertTrue(callable(fn_o))

    async def test_mcp_lightrag_server_role_routing_and_trace(self) -> None:
        import mcp_lightrag_server  # noqa: E402

        called_ollama: list[tuple[str, str]] = []

        async def _fake_ollama_chat(prompt, system_prompt=None, history_messages=None, model_name=None, **kwargs):
            called_ollama.append((prompt, model_name))
            return "Synthese locale validee"

        class _FakeMCPRag:
            async def aquery(self, query, param):
                return await mcp_lightrag_server.llm_func(query)

            async def aquery_data(self, query, param):
                return {
                    "status": "success",
                    "data": {"chunks": [{"file_path": "doc.md", "content": "contenu", "rerank_score": 0.9}]},
                }

        async def _get_fake_rag():
            return _FakeMCPRag()

        # Verifie les valeurs par defaut MCP : llm_mode='auto' et provider='auto' + support '1minai'
        tools_by_name = {t.name: t for t in mcp_lightrag_server.TOOLS}
        for tname in ("rag_search", "rag_analyze_impact", "rag_audit_integrity"):
            props = tools_by_name[tname].inputSchema["properties"]
            self.assertEqual(props["llm_mode"]["default"], "auto", tname)
            self.assertIn("1minai", props["provider"]["enum"], tname)

        # 1) Sans Gemini ni 1min.ai, rag_search ET rag_analyze_impact replient sur Ollama gemma4:26b
        with patch.dict(os.environ, {"ONEMINAI_API_KEY": ""}, clear=False), patch.object(
            mcp_lightrag_server, "get_rag", side_effect=_get_fake_rag
        ), patch.object(
            mcp_lightrag_server, "get_genai_client", return_value=None
        ), patch.object(
            mcp_lightrag_server, "check_ollama_ready", side_effect=lambda url, required_model=None, timeout=0.4: required_model in (None, "gemma4:26b", "qwen3.8:27b-mlx")
        ), patch.object(
            mcp_lightrag_server, "check_unsloth_ready", return_value=False
        ), patch.object(
            mcp_lightrag_server, "_call_ollama_chat", side_effect=_fake_ollama_chat
        ):
            # Appel bare sans llm_mode -> utilise 'auto' par defaut
            res_search = await mcp_lightrag_server.call_tool(
                "rag_search", {"query": "couple RS-06"}
            )
            res_impact = await mcp_lightrag_server.call_tool(
                "rag_analyze_impact", {"scenario": "hausse masse torse"}
            )
            res_antigrav = await mcp_lightrag_server.call_tool(
                "rag_search", {"query": "couple RS-06", "llm_mode": "antigravity"}
            )

        # 2) Avec ONEMINAI_API_KEY, rag_search en mode par defaut ('auto') passe par 1min.ai mistral-small-2603 sans demarrer Ollama
        mcp_lightrag_server._ONEMINAI_SESSIONS.clear()
        with patch.dict(
            os.environ, {"ONEMINAI_API_KEY": "mcp-qa-key", "ONEMINAI_QA_MODEL": ""}, clear=False
        ), patch.object(
            mcp_lightrag_server, "get_rag", side_effect=_get_fake_rag
        ), patch.object(
            mcp_lightrag_server, "get_genai_client", return_value=None
        ), patch.object(
            rag_runtime, "call_1minai_stateless_async", return_value=("Synthese MCP 1minai", 200, 40)
        ) as mock_1min, patch.object(
            mcp_lightrag_server, "_call_ollama_chat"
        ) as mock_ol_skipped:
            res_1min = await mcp_lightrag_server.call_tool("rag_search", {"query": "jeu RB8016"})
            res_audit_1min = await mcp_lightrag_server.call_tool(
                "rag_audit_integrity", {"scope": "cinematique_moteurs", "save_report": False}
            )
            mock_ol_skipped.assert_not_called()
        self.assertIn("1minai / mistral-small-2603", res_1min[0].text)
        self.assertIn("1minai / mistral-small-2603", res_audit_1min[0].text)
        self.assertEqual(mock_1min.call_args.args[0], "mistral-small-2603")

        # 3) Sous llm_mode='auto' (defaut), si tous les backends LLM echouent, repli transparent Antigravity
        mcp_lightrag_server._ONEMINAI_SESSIONS.clear()
        with patch.dict(
            os.environ, {"ONEMINAI_API_KEY": "", "OPENROUTER_API_KEY": ""}, clear=False
        ), patch.object(
            mcp_lightrag_server, "get_rag", side_effect=_get_fake_rag
        ), patch.object(
            mcp_lightrag_server, "get_genai_client", return_value=None
        ), patch.object(
            mcp_lightrag_server, "check_ollama_ready", return_value=False
        ), patch.object(
            mcp_lightrag_server, "check_unsloth_ready", return_value=False
        ):
            res_auto_fallback = await mcp_lightrag_server.call_tool("rag_search", {"query": "jeu RB8016"})
        self.assertIn("repli antigravity", res_auto_fallback[0].text)

        # 4) Verifie que rag_cli.py expose --llm-mode auto par defaut et supporte 1minai
        rag_cli_src = Path(_RAG_DIR, "rag_cli.py").read_text(encoding="utf-8")
        self.assertIn('default="auto"', rag_cli_src)
        self.assertIn('"1minai"', rag_cli_src)

        class _FakeMCPRagCached:
            async def aquery(self, query, param):
                return "Réponse servie depuis le cache LightRAG"

        async def _get_fake_rag_cached():
            return _FakeMCPRagCached()

        with patch.object(mcp_lightrag_server, "get_rag", side_effect=_get_fake_rag_cached):
            res_cached = await mcp_lightrag_server.call_tool(
                "rag_search", {"query": "couple RS-06", "llm_mode": "internal"}
            )

        self.assertEqual(called_ollama[0], ("couple RS-06", "gemma4:26b"))
        self.assertEqual(called_ollama[1], ("hausse masse torse", "gemma4:26b"))
        self.assertIn("ollama / gemma4:26b", res_search[0].text)
        self.assertIn("ollama / gemma4:26b", res_impact[0].text)
        self.assertIn("Aucun LLM", res_antigrav[0].text)
        self.assertIn("Cache LightRAG (réponse en cache — 0 appel LLM [mode internal])", res_cached[0].text)

    def test_1minai_config_and_never_in_auto_cascade(self) -> None:
        clean_env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("ONEMINAI_MODEL", "ONEMINAI_QA_MODEL", "ONEMINAI_AUDIT_MODEL")
        }
        with patch.dict(os.environ, clean_env, clear=True):
            self.assertEqual(rag_runtime.resolve_1minai_config()[1], "mistral-small-latest")
            self.assertEqual(rag_runtime.resolve_1minai_config("index")[1], "mistral-small-latest")
            self.assertEqual(rag_runtime.resolve_1minai_config("qa")[1], "mistral-small-2603")
            self.assertEqual(rag_runtime.resolve_1minai_config("audit")[1], "mistral-small-2603")
        self.assertTrue(rag_runtime.is_1minai_temperature_omitted("deepseek-flash"))
        self.assertTrue(rag_runtime.is_1minai_temperature_omitted("gpt-5-nano"))
        self.assertTrue(rag_runtime.is_1minai_temperature_omitted("gpt-5.4-nano"))
        self.assertTrue(rag_runtime.is_1minai_temperature_omitted("gpt-6-luna"))
        self.assertFalse(rag_runtime.is_1minai_temperature_omitted("mistral-small-latest"))
        self.assertFalse(rag_runtime.is_1minai_compatible_model_override("gemma4:26b"))
        self.assertTrue(rag_runtime.is_1minai_compatible_model_override("mistral-small-2603"))
        capped_init = rag_runtime.build_1minai_chat_payload(
            "mistral-small-latest",
            [{"role": "user", "content": "hi"}],
            temperature=0.1,
            max_tokens=8192,
        )
        self.assertEqual(capped_init["max_tokens"], 4096)

        with patch.dict(
            os.environ,
            {
                "ONEMINAI_API_KEY": "test-1min-key",
                "ONEMINAI_BASE_URL": "https://api.1min.ai",
                "ONEMINAI_MODEL": "qwen3.7-flash",
                "ONEMINAI_QA_MODEL": "",
                "ONEMINAI_AUDIT_MODEL": "",
            },
            clear=False,
        ):
            base_url, model, key = rag_runtime.resolve_1minai_config("index")
            self.assertEqual(base_url, "https://api.1min.ai/openai/v1")
            self.assertEqual(model, "qwen3.7-flash")
            self.assertEqual(key, "test-1min-key")

            with patch.object(rag_runtime, "check_ollama_ready", return_value=False), patch.object(
                rag_runtime, "check_unsloth_ready", return_value=False
            ):
                # En mode auto index sans Gemini ni OpenRouter ni local, auto NE doit PAS depenser 1min.ai
                self.assertIsNone(
                    rag_runtime.resolve_active_provider("auto", gemini_key="", openrouter_key="", role="index")
                )
                # En QA/Audit sans Gemini ni local, auto bascule bien vers 1min.ai (puis gemma4:26b)
                self.assertEqual(
                    rag_runtime.resolve_active_provider("auto", gemini_key="", openrouter_key="", role="qa"),
                    "1minai",
                )
                self.assertEqual(
                    rag_runtime.resolve_active_provider("auto", gemini_key="", openrouter_key="", role="audit"),
                    "1minai",
                )
                # En mode explicite --provider 1minai, il est bien resolu
                self.assertEqual(rag_runtime.resolve_active_provider("1minai"), "1minai")

    async def test_index_docs_1minai_stateless_openai_and_token_accounting(self) -> None:
        captured: list[dict] = []

        async def _fake_post(url, payload, **kwargs):
            captured.append({"url": url, "payload": payload, "headers": kwargs.get("headers")})
            return {
                "choices": [{"message": {"content": "entites extraites"}}],
                "usage": {"prompt_tokens": 1200, "completion_tokens": 350, "total_tokens": 1550},
            }

        with patch.dict(os.environ, {"ONEMINAI_API_KEY": "fake-1min-key"}, clear=False), patch.object(
            index_docs, "_post_json_aiohttp", side_effect=_fake_post
        ):
            args = index_docs.parse_cli_args(["--provider", "1minai", "--model", "deepseek-flash"])
            fn = await index_docs.get_llm_func(args)
            res = await fn("chunk contenu", system_prompt="sys prompt", hashing_kv={"ignored": True})

        self.assertEqual(res, "entites extraites")
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0]["url"], "https://api.1min.ai/openai/v1/chat/completions")
        self.assertEqual(captured[0]["payload"]["model"], "deepseek-flash")
        self.assertNotIn("temperature", captured[0]["payload"])
        self.assertEqual(captured[0]["headers"]["Authorization"], "Bearer fake-1min-key")
        self.assertNotIn("hashing_kv", captured[0]["payload"])
        s = index_docs.stats["1minai:deepseek-flash"]
        self.assertEqual(s["success"], 1)
        self.assertEqual(s["prompt_tokens"], 1200)
        self.assertEqual(s["completion_tokens"], 350)

    async def test_1minai_http400_omit_temperature_and_max_tokens_adaptation(self) -> None:
        rag_runtime.reset_1minai_model_quirks()
        try:
            seen_payloads: list[dict] = []

            async def _adaptive_fake_post(url, payload, **kwargs):
                seen_payloads.append(dict(payload))
                if len(seen_payloads) == 1:
                    raise RuntimeError(
                        '1min.ai HTTP 400: {"error":{"message":"Omit temperature for this model.",'
                        '"type":"invalid_request_error","param":"temperature","code":"invalid_request_error"}}'
                    )
                if len(seen_payloads) == 2:
                    raise RuntimeError(
                        "1min.ai HTTP 400: {'error': {'message': \"Unsupported parameter: 'max_tokens'. "
                        "Use 'max_completion_tokens' instead.\", 'param': 'max_tokens'}}"
                    )
                return {
                    "choices": [{"message": {"content": "extraction adaptee OK"}}],
                    "usage": {"prompt_tokens": 500, "completion_tokens": 120, "total_tokens": 620},
                }

            with patch.dict(os.environ, {"ONEMINAI_API_KEY": "fake-1min-key"}, clear=False), patch.object(
                index_docs, "_post_json_aiohttp", side_effect=_adaptive_fake_post
            ):
                args = index_docs.parse_cli_args(["--provider", "1minai", "--model", "gpt-5.6-luna"])
                fn = await index_docs.get_llm_func(args)
                res = await fn("chunk test")

            self.assertEqual(res, "extraction adaptee OK")
            self.assertEqual(len(seen_payloads), 3)
            self.assertIn("temperature", seen_payloads[0])
            self.assertNotIn("temperature", seen_payloads[1])
            self.assertIn("max_tokens", seen_payloads[1])
            self.assertNotIn("temperature", seen_payloads[2])
            self.assertNotIn("max_tokens", seen_payloads[2])
            self.assertEqual(seen_payloads[2]["max_completion_tokens"], 8192)

            # La contrainte apprise est memorisee pour les appels suivants sur gpt-5.6-luna
            next_payload = rag_runtime.build_1minai_chat_payload(
                "gpt-5.6-luna",
                [{"role": "user", "content": "hi"}],
                temperature=0.1,
                max_tokens=1024,
            )
            self.assertNotIn("temperature", next_payload)
            self.assertNotIn("max_tokens", next_payload)
            self.assertEqual(next_payload["max_completion_tokens"], 1024)

            # Test du plafonnement dynamique (cas reel mistral-small-latest max_completion_tokens=4096)
            cap_payloads: list[dict] = []

            async def _capped_fake_post(url, payload, **kwargs):
                cap_payloads.append(dict(payload))
                if len(cap_payloads) == 1:
                    raise RuntimeError(
                        '1min.ai HTTP 400: {"error":{"message":"Output limit exceeds the model maximum of 4096.",'
                        '"type":"invalid_request_error","param":"max_completion_tokens","code":"invalid_request_error"}}'
                    )
                return {
                    "choices": [{"message": {"content": "cap 4096 OK"}}],
                    "usage": {"prompt_tokens": 300, "completion_tokens": 80, "total_tokens": 380},
                }

            with patch.dict(os.environ, {"ONEMINAI_API_KEY": "fake-1min-key"}, clear=False), patch.object(
                index_docs, "_post_json_aiohttp", side_effect=_capped_fake_post
            ):
                args_cap = index_docs.parse_cli_args(["--provider", "1minai", "--model", "mistral-small-test"])
                fn_cap = await index_docs.get_llm_func(args_cap)
                res_cap = await fn_cap("chunk mistral")

            self.assertEqual(res_cap, "cap 4096 OK")
            self.assertEqual(cap_payloads[0]["max_tokens"], 8192)
            self.assertEqual(cap_payloads[1]["max_tokens"], 4096)
            next_cap = rag_runtime.build_1minai_chat_payload(
                "mistral-small-test",
                [{"role": "user", "content": "hi"}],
                temperature=0.1,
                max_tokens=8192,
            )
            self.assertEqual(next_cap["max_tokens"], 4096)

            # Test de call_openai_chat_adaptive_async (ask_rag / check_integrity)
            sdk_calls: list[dict] = []

            class _FakeCompletions:
                async def create(self, **kwargs):
                    sdk_calls.append(dict(kwargs))
                    if len(sdk_calls) == 1:
                        err = RuntimeError("HTTP 400 Omit temperature for this model.")
                        err.body = {
                            "error": {
                                "message": "Omit temperature for this model.",
                                "type": "invalid_request_error",
                                "param": "temperature",
                            }
                        }
                        raise err
                    msg = MagicMock()
                    msg.content = "Reponse OK"
                    choice = MagicMock()
                    choice.message = msg
                    resp = MagicMock()
                    resp.choices = [choice]
                    return resp

            fake_client = MagicMock()
            fake_client.chat.completions = _FakeCompletions()
            sdk_resp = await rag_runtime.call_openai_chat_adaptive_async(
                fake_client,
                "gpt-5-mini",
                [{"role": "user", "content": "hello"}],
                temperature=0.7,
                max_tokens=256,
            )
            self.assertEqual(sdk_resp.choices[0].message.content, "Reponse OK")
            self.assertIn("temperature", sdk_calls[0])
            self.assertNotIn("temperature", sdk_calls[1])

            # Test check_1minai.py --test-model sur modele rejetant temperature dynamiquement
            post_calls: list[dict] = []

            def _fake_requests_post(url, headers=None, json=None, timeout=None):
                post_calls.append(dict(json or {}))
                if len(post_calls) == 1:
                    return _MockHTTPResponse(
                        400,
                        text='{"error":{"message":"Omit temperature for this model.","param":"temperature"}}',
                    )
                return _MockHTTPResponse(
                    200,
                    payload={
                        "choices": [{"message": {"content": "OK"}}],
                        "usage": {"prompt_tokens": 12, "completion_tokens": 2, "total_tokens": 14},
                    },
                )

            with patch.dict(os.environ, {"ONEMINAI_API_KEY": "fake-1min-key"}, clear=False), patch.object(
                check_1minai, "fetch_1minai_models", return_value=["qwen3.7-flash", "deepseek-flash", "o3"]
            ), patch.object(check_1minai.requests, "post", side_effect=_fake_requests_post):
                rag_runtime.reset_1minai_model_quirks()
                rc = check_1minai.check_1minai(test_model="gpt-5.4-mini")
            self.assertEqual(rc, 0)
            self.assertEqual(len(post_calls), 2)
            self.assertIn("temperature", post_calls[0])
            self.assertNotIn("temperature", post_calls[1])
        finally:
            rag_runtime.reset_1minai_model_quirks()

    async def test_index_docs_auto_3tier_gemini_then_1minai_then_ollama(self) -> None:
        started: list[str] = []

        class _FakeManagedOllama:
            def __init__(self, base_url=None, model=None) -> None:
                self.base_url = base_url or "http://127.0.0.1:11434"
                self.model = model or "qwen3.8:27b-mlx"

            def ensure_started(self, timeout_s: float = 15.0) -> bool:
                started.append(self.model)
                return True

        # 1) Par defaut en auto: 0 credit 1min.ai meme si ONEMINAI_API_KEY est present
        with patch.dict(
            os.environ,
            {"ONEMINAI_API_KEY": "fake-1min-key", "ONEMINAI_MODEL": "o3", "RAG_AUTO_1MINAI": "0"},
            clear=False,
        ):
            enabled_default, _, _, _ = rag_runtime.resolve_1minai_auto_index_target()
            self.assertFalse(enabled_default)

        # 2) Opt-in (--with-1minai / allow_1minai=True) + verrou anti-facture qwen3.7-flash
        with patch.dict(
            os.environ,
            {"ONEMINAI_API_KEY": "fake-1min-key", "ONEMINAI_MODEL": "o3", "RAG_AUTO_ALLOW_PAID_1MINAI": "0"},
            clear=False,
        ):
            enabled, _, auto_model, _ = rag_runtime.resolve_1minai_auto_index_target(allow_1minai=True)
            self.assertTrue(enabled)
            self.assertEqual(auto_model, "qwen3.7-flash")

            # Et index (resolve_active_provider) continue d'ignorer 1minai, tandis que qa/audit l'activent
            with patch.object(rag_runtime, "check_ollama_ready", return_value=False), patch.object(
                rag_runtime, "check_unsloth_ready", return_value=False
            ):
                self.assertIsNone(
                    rag_runtime.resolve_active_provider("auto", gemini_key="", openrouter_key="", role="index")
                )
                self.assertEqual(
                    rag_runtime.resolve_active_provider("auto", gemini_key="", openrouter_key="", role="qa"),
                    "1minai",
                )

        # 3) Gemini epuise + --with-1minai -> palier 2 1min.ai (qwen3.7-flash) repond sans demarrer Ollama
        seen_urls: list[tuple[str, str | None]] = []

        async def _post_tier2_then_tier3(url, payload, **kwargs):
            seen_urls.append((url, payload.get("model")))
            if url.endswith("/chat/completions"):
                if len(seen_urls) == 1:
                    return {
                        "choices": [{"message": {"content": "entites via 1minai"}}],
                        "usage": {"prompt_tokens": 900, "completion_tokens": 210, "total_tokens": 1110},
                    }
                raise RuntimeError('1min.ai HTTP 402: {"error":{"message":"Insufficient credits"}}')
            return {"message": {"content": "entites via ollama final"}}

        managed = _FakeManagedOllama(model="qwen3.8:27b-mlx")
        args = index_docs.parse_cli_args(["--provider", "auto", "--with-1minai"])
        with patch.dict(
            os.environ,
            {"ONEMINAI_API_KEY": "fake-1min-key", "ONEMINAI_MODEL": "o3", "RAG_AUTO_ALLOW_PAID_1MINAI": "0"},
            clear=False,
        ):
            state = index_docs._create_auto_state(args, api_key="dummy-gem-key", managed_ollama=managed)
            with patch.object(index_docs, "_create_genai_client", return_value=object()), patch.object(
                index_docs, "_call_gemini_cascade", return_value=(None, None)
            ) as mock_gem, patch.object(
                index_docs, "_check_ollama_ready", side_effect=[(False, "stopped"), (True, "OK")]
            ), patch.object(
                index_docs, "_post_json_aiohttp", side_effect=_post_tier2_then_tier3
            ):
                async def _gem_exhaust(*a, **k):
                    state["cloud_exhausted"] = True
                    return None, None

                mock_gem.side_effect = _gem_exhaust
                fn = await index_docs.get_llm_func(args, auto_state=state, managed_ollama=managed)

                # Chunk 1 : Gemini echoue -> 1min.ai reussit -> Ollama jamais lance
                r1 = await fn("chunk 1")
                self.assertEqual(r1, "entites via 1minai")
                self.assertEqual(started, [])
                self.assertEqual(state["oneminai_ok"], 1)
                self.assertEqual(state["oneminai_prompt_tokens"], 900)
                self.assertEqual(state["oneminai_completion_tokens"], 210)
                self.assertEqual(seen_urls[0], ("https://api.1min.ai/openai/v1/chat/completions", "qwen3.7-flash"))

                # Chunk 2 : 1min.ai renvoie HTTP 402 -> bascule definitive sur dernier repli Ollama
                r2 = await fn("chunk 2")
                self.assertEqual(r2, "entites via ollama final")
                self.assertTrue(state["oneminai_exhausted"])
                self.assertEqual(state["oneminai_err"], 1)
                self.assertEqual(state["ollama_ok"], 1)
                self.assertEqual(started, ["qwen3.8:27b-mlx"])

        # 4) Sans --with-1minai (ou avec --no-1minai), le palier 2 est desactive par defaut
        with patch.dict(os.environ, {"ONEMINAI_API_KEY": "fake-1min-key"}, clear=False):
            os.environ.pop("RAG_AUTO_1MINAI", None)
            args_def = index_docs.parse_cli_args(["--provider", "auto"])
            state_def = index_docs._create_auto_state(args_def, api_key="", managed_ollama=managed)
            self.assertFalse(state_def["oneminai_enabled"])
            self.assertTrue(state_def["oneminai_exhausted"])
            args_no_1m = index_docs.parse_cli_args(["--provider", "auto", "--with-1minai", "--no-1minai"])
            state_no_1m = index_docs._create_auto_state(args_no_1m, api_key="", managed_ollama=managed)
            self.assertFalse(state_no_1m["oneminai_enabled"])
            self.assertTrue(state_no_1m["oneminai_exhausted"])

    async def test_mcp_rag_index_document_auto_3tier_and_search_unchanged(self) -> None:
        import mcp_lightrag_server  # noqa: E402

        called_1minai: list[tuple[str, str]] = []

        async def _fake_1minai(model, messages, **kwargs):
            called_1minai.append((model, str(kwargs.get("api_key"))))
            return "Index MCP OK via 1minai", 400, 90

        class _FakeDocStatus:
            _storage_lock = mcp_lightrag_server.asyncio.Lock()
            _data = {}

            async def get_by_id(self, doc_id: str):
                return {"status": "processed", "file_path": "sample.md"}

        class _FakeMCPIndexRag:
            def __init__(self) -> None:
                self.doc_status = _FakeDocStatus()
                self.full_docs = None
                self.llm_model_func = None

            async def initialize_storages(self) -> None:
                return None

            async def ainsert(self, content: str, ids=None, file_paths=None) -> None:
                res = await self.llm_model_func("extrait entites MCP")
                assert res == "Index MCP OK via 1minai"

        fake_rag = _FakeMCPIndexRag()

        async def _get_fake_rag():
            return fake_rag

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            doc = tmp_path / "sample.md"
            doc.write_text("# Test MCP", encoding="utf-8")
            db_dir = tmp_path / "db"
            db_dir.mkdir()
            with patch.dict(
                os.environ,
                {"ONEMINAI_API_KEY": "mcp-1min-key", "ONEMINAI_MODEL": "deepseek-flash", "RAG_AUTO_1MINAI": "true"},
                clear=False,
            ), patch.object(
                mcp_lightrag_server, "DOCS_ROOT", tmp_path
            ), patch.object(mcp_lightrag_server, "DB_PATH", db_dir), patch.object(
                mcp_lightrag_server, "get_rag", side_effect=_get_fake_rag
            ), patch.object(
                mcp_lightrag_server, "_call_gemini_chat", return_value=(None, None)
            ), patch.object(
                mcp_lightrag_server, "call_1minai_stateless_async", side_effect=_fake_1minai
            ), patch.object(
                mcp_lightrag_server, "_call_ollama_chat"
            ) as mock_ol:
                res = await mcp_lightrag_server.call_tool(
                    "rag_index_document", {"file_path": "sample.md", "provider": "auto"}
                )
                mock_ol.assert_not_called()

        self.assertEqual(called_1minai, [("qwen3.7-flash", "mcp-1min-key")])
        self.assertIn("1min.ai (qwen3.7-flash)", res[0].text)
        self.assertIn("1minai / qwen3.7-flash", res[0].text)

    async def test_agent_indexing_effort_linter_and_e2e_mcp_commit(self) -> None:
        import numpy as np
        from lightrag import LightRAG  # noqa: E402
        from lightrag.utils import EmbeddingFunc  # noqa: E402
        import agent_indexing  # noqa: E402
        import mcp_lightrag_server  # noqa: E402

        # 1) Classification effort / thinking adapte (jamais extra_high)
        self.assertEqual(
            agent_indexing.classify_chunk_effort("notes/audio_test.md", "Simple texte sur STT.", "balanced")[:2],
            ("flash", "low"),
        )
        self.assertEqual(
            agent_indexing.classify_chunk_effort("01_Mecanique_et_Chassis/FINAL_BOM_Torse.md", "Simple texte", "balanced")[:2],
            ("inherit", "medium"),
        )
        dense_table = "| Col | Val |\n| :--- | :--- |\n| A | 10 mm |\n| B | 20 mm |"
        self.assertEqual(
            agent_indexing.classify_chunk_effort("docs/table.md", dense_table, "balanced")[:2],
            ("inherit", "medium"),
        )
        self.assertEqual(
            agent_indexing.classify_chunk_effort("FINAL_BOM.md", dense_table, "fast")[:2],
            ("flash", "low"),
        )
        for p_cfg in agent_indexing.AGENT_EFFORT_PROFILES.values():
            self.assertNotIn(p_cfg["gemini_thinking_level"], ("extra_high",))

        # 2) Linter strict (<|#|>, <|COMPLETE|>, 0 dollar/LaTeX)
        self.assertTrue(agent_indexing.validate_single_extraction("entity<|#|>RS-04<|#|>Moteur<|#|>QDD\n<|COMPLETE|>") == [])
        self.assertTrue(any("COMPLETE" in e for e in agent_indexing.validate_single_extraction("entity<|#|>RS-04<|#|>Moteur<|#|>QDD")))
        self.assertTrue(any("dollar" in e for e in agent_indexing.validate_single_extraction("entity<|#|>A<|#|>T<|#|>10 $ mm\n<|COMPLETE|>")))
        self.assertTrue(any("entity" in e for e in agent_indexing.validate_single_extraction("entity<|#|>Seul<|#|>Type\n<|COMPLETE|>")))

        # 3) Fusion deterministe sans LLM tiers (summarize_entity_descriptions)
        merged = agent_indexing.deterministic_merge_descriptions(
            "---Task---\nEntity Name: RS-04\n\nDescription List:\n```\n"
            '{"description": "Moteur QDD epaule 48 V."}\n'
            '{"description": "Moteur QDD epaule 48 V."}\n'
            '{"description": "Couple nominal 40 Nm et bride 7075-T6."}\n'
            "```\n"
        )
        self.assertIn("Moteur QDD epaule 48 V.", merged)
        self.assertEqual(merged.count("Moteur QDD epaule 48 V."), 1)
        self.assertIn("Couple nominal 40 Nm", merged)

        # 4) Pipeline complet MCP rag_prepare_agent_index -> rag_commit_agent_index sur vrai LightRAG (0 LLM tiers)
        tools_by_name = {t.name: t for t in mcp_lightrag_server.TOOLS}
        self.assertIn("rag_prepare_agent_index", tools_by_name)
        self.assertIn("rag_commit_agent_index", tools_by_name)

        async def _fake_embed(texts: list[str]) -> np.ndarray:
            vecs = []
            for idx, txt in enumerate(texts):
                h = sum(ord(ch) for ch in txt) % 1000
                vecs.append([float((h + j) % 97) / 97.0 + 0.01 for j in range(8)])
            return np.array(vecs, dtype=np.float32)

        bomb_calls: list[str] = []

        async def _bomb_llm(prompt, system_prompt=None, history_messages=None, **kwargs):
            bomb_calls.append(str(prompt)[:40])
            raise AssertionError("Aucun LLM tiers ne doit etre appele pendant commit_agent_bundle !")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            docs_dir = tmp_path / "docs"
            db_dir = tmp_path / "db"
            docs_dir.mkdir()
            db_dir.mkdir()

            (docs_dir / "note_simple.md").write_text("# Note Bus\nLe bus CAN-FD utilise 1 Mbps sur 5 bus.", encoding="utf-8")
            (docs_dir / "FINAL_Torse.md").write_text("# Torse\nLe roulement RB8016 supporte l'axe RS-06 du waist.", encoding="utf-8")
            (docs_dir / "schema.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg"><title>Plan Torse</title><text>Vis 91292A130</text></svg>',
                encoding="utf-8",
            )
            (docs_dir / "vue.png").write_bytes(b"\x89PNG\r\n\x1a\n")

            rag_real = LightRAG(
                working_dir=str(db_dir),
                llm_model_func=_bomb_llm,
                embedding_func=EmbeddingFunc(embedding_dim=8, max_token_size=8192, func=_fake_embed),
                chunk_token_size=1600,
                chunk_overlap_token_size=150,
                llm_model_max_async=1,
                addon_params={"language": "French"},
            )
            await rag_real.initialize_storages()

            async def _get_real_rag():
                return rag_real

            with patch.object(mcp_lightrag_server, "DOCS_ROOT", docs_dir), patch.object(
                mcp_lightrag_server, "DB_PATH", db_dir
            ), patch.object(mcp_lightrag_server, "get_rag", side_effect=_get_real_rag):
                prep_res = await mcp_lightrag_server.call_tool(
                    "rag_prepare_agent_index", {"effort_profile": "balanced"}
                )
                prep_data = json.loads(prep_res[0].text)
                self.assertEqual(prep_data["effort_profile"], "balanced")
                self.assertEqual(prep_data["chunks_count"], 3)
                self.assertEqual(prep_data["images_count"], 1)

                by_doc = {c["doc_rel"]: c for c in prep_data["chunks"]}
                self.assertEqual(by_doc["note_simple.md"]["recommended_subagent_model"], "flash")
                self.assertEqual(by_doc["schema.svg"]["recommended_subagent_model"], "flash")
                self.assertEqual(by_doc["FINAL_Torse.md"]["recommended_subagent_model"], "inherit")
                self.assertEqual(prep_data["images"][0]["recommended_subagent_model"], "inherit")

                extractions_inline = {
                    "chunk_extractions": {
                        by_doc["note_simple.md"]["chunk_hash"]: (
                            "entity<|#|>CAN-FD<|#|>Protocol<|#|>Bus communication principal a 1 Mbps sur 5 bus.\n"
                            "<|COMPLETE|>"
                        ),
                        by_doc["FINAL_Torse.md"]["chunk_hash"]: (
                            "entity<|#|>RB8016<|#|>Component<|#|>Roulement a rouleaux croises du waist.\n"
                            "entity<|#|>RS-06<|#|>Hardware<|#|>Actionneur QDD du waist.\n"
                            "relation<|#|>RS-06<|#|>RB8016<|#|>entraine,axe<|#|>RS-06 actionne la rotation guidee par RB8016.\n"
                            "<|COMPLETE|>"
                        ),
                        by_doc["schema.svg"]["chunk_hash"]: (
                            "entity<|#|>91292A130<|#|>Part<|#|>Vis CHC M4x30 McMaster-Carr sur schema torse.\n"
                            "<|COMPLETE|>"
                        ),
                    },
                    "vlm_descriptions": {
                        "vue.png": "Vue technique de la bride d'epaule avec roulement RB8016 et 4 vis M4.",
                    },
                    "vlm_extractions": {
                        "vue.png": (
                            "entity<|#|>Bride Epaule<|#|>Component<|#|>Piece structurelle en 7075-T6 vue sur CAO.\n"
                            "<|COMPLETE|>"
                        ),
                    },
                }
                commit_res = await mcp_lightrag_server.call_tool(
                    "rag_commit_agent_index",
                    {"job_id": prep_data["job_id"], "extractions": extractions_inline},
                )

            self.assertEqual(bomb_calls, [])
            commit_txt = commit_res[0].text
            self.assertIn("antigravity / self-agent", commit_txt)
            self.assertIn("Documents indexés (4)", commit_txt)
            self.assertIn("Chunks rejoués", commit_txt)
            self.assertFalse((db_dir / ".agent_jobs" / prep_data["job_id"]).exists())

            idx_json = json.loads((db_dir / "indexed_files.json").read_text(encoding="utf-8"))
            self.assertEqual(len(idx_json), 4)
            full_ents = json.loads((db_dir / "kv_store_full_entities.json").read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(full_ents), 4)

            # Re-prepare immediat -> 0 fichier a reindexer
            with patch.object(mcp_lightrag_server, "DOCS_ROOT", docs_dir), patch.object(
                mcp_lightrag_server, "DB_PATH", db_dir
            ):
                prep_clean = await mcp_lightrag_server.call_tool(
                    "rag_prepare_agent_index", {"effort_profile": "balanced"}
                )
            self.assertEqual(json.loads(prep_clean[0].text)["chunks_count"], 0)

        # 5) Verifie flags CLI index_docs & rag_cli
        cli_prep = index_docs.parse_cli_args(["--prepare-agent", "--effort-profile", "balanced"])
        self.assertEqual(cli_prep.prepare_agent, "auto")
        self.assertEqual(cli_prep.effort_profile, "balanced")
        self.assertFalse(cli_prep.update)
        cli_commit = index_docs.parse_cli_args(["--commit-agent", "job_test", "--extractions", "ext.json"])
        self.assertEqual(cli_commit.commit_agent, "job_test")
        self.assertEqual(cli_commit.extractions, "ext.json")
        rag_cli_src = Path(_RAG_DIR, "rag_cli.py").read_text(encoding="utf-8")
        self.assertIn("--prepare-agent", rag_cli_src)
        self.assertIn("--commit-agent", rag_cli_src)

    async def test_mcp_disk_auto_reload_and_external_indexing_lock(self) -> None:
        import agent_indexing  # noqa: E402
        import mcp_lightrag_server  # noqa: E402

        created_instances: list[object] = []

        class _FakeReloadableLightRAG:
            def __init__(self, **kwargs) -> None:
                self.kwargs = kwargs
                self.init_calls = 0
                self.finalize_calls = 0
                created_instances.append(self)

            async def initialize_storages(self) -> None:
                self.init_calls += 1

            async def finalize_storages(self) -> None:
                self.finalize_calls += 1

        with tempfile.TemporaryDirectory() as tmp_dir:
            db_dir = Path(tmp_dir) / "db"
            db_dir.mkdir()
            idx_file = db_dir / "indexed_files.json"
            idx_file.write_text('{"a.md": {"mtime": 1, "doc_id": "doc-1"}}', encoding="utf-8")

            saved_inst = mcp_lightrag_server._rag_instance
            saved_path = mcp_lightrag_server._rag_disk_path
            saved_stamp = mcp_lightrag_server._rag_disk_stamp
            mcp_lightrag_server._rag_instance = None
            mcp_lightrag_server._rag_disk_path = None
            mcp_lightrag_server._rag_disk_stamp = None
            try:
                with patch.object(mcp_lightrag_server, "DB_PATH", db_dir), patch.object(
                    mcp_lightrag_server, "LightRAG", _FakeReloadableLightRAG
                ):
                    r1 = await mcp_lightrag_server.get_rag()
                    self.assertEqual(len(created_instances), 1)
                    self.assertEqual(r1.init_calls, 1)

                    # Sans changement disque -> meme instance en cache
                    r1_cached = await mcp_lightrag_server.get_rag()
                    self.assertIs(r1_cached, r1)
                    self.assertEqual(len(created_instances), 1)

                    # Pendant un verrou externe actif, get_rag garde l'instance stable et commit est bloque
                    lock = agent_indexing.IndexingFileLock(db_dir).acquire()
                    try:
                        self.assertTrue(agent_indexing.is_indexing_lock_active(db_dir))
                        with self.assertRaises(RuntimeError):
                            agent_indexing.IndexingFileLock(db_dir).acquire()
                        idx_file.write_text(
                            '{"a.md": {"mtime": 1, "doc_id": "doc-1"}, "b.md": {"mtime": 2, "doc_id": "doc-2"}}',
                            encoding="utf-8",
                        )
                        r_locked = await mcp_lightrag_server.get_rag()
                        self.assertIs(r_locked, r1)
                        self.assertEqual(len(created_instances), 1)

                        blocked = await mcp_lightrag_server.call_tool(
                            "rag_commit_agent_index", {"job_id": "job_dummy"}
                        )
                        self.assertIn("indexation externe", blocked[0].text.lower())
                    finally:
                        lock.release()

                    self.assertFalse(agent_indexing.is_indexing_lock_active(db_dir))

                    # Une fois le verrou relache, get_rag detecte le nouveau mtime/taille et recharge
                    r2 = await mcp_lightrag_server.get_rag()
                    self.assertIsNot(r2, r1)
                    self.assertEqual(len(created_instances), 2)
                    self.assertEqual(r1.finalize_calls, 1)
                    self.assertEqual(r2.init_calls, 1)

                    # Re-appel immediat apres rechargement -> plus de rechargement inutile
                    r2_cached = await mcp_lightrag_server.get_rag()
                    self.assertIs(r2_cached, r2)
                    self.assertEqual(len(created_instances), 2)
            finally:
                mcp_lightrag_server._rag_instance = saved_inst
                mcp_lightrag_server._rag_disk_path = saved_path
                mcp_lightrag_server._rag_disk_stamp = saved_stamp

    def test_markdown_anchored_chunking_stability_fences_and_tables(self) -> None:
        from lightrag.lightrag import chunking_by_token_size  # noqa: E402
        from lightrag.utils import TiktokenTokenizer  # noqa: E402
        import hashlib  # noqa: E402
        import rag_chunking  # noqa: E402

        tok = TiktokenTokenizer()
        sections = [
            f"## {idx}. Sous-ensemble {idx}\n"
            + "\n".join(
                f"Parametre {idx}.{j} = {10 * idx + j}.5 mm sur bride AL7075-T6 et moteur RS-0{(idx % 6) + 1}."
                for j in range(1, 24)
            )
            for idx in range(1, 7)
        ]
        # Ajoute un bloc code contenant de faux titres ## et un grand tableau Markdown
        sections[2] += (
            "\n\n```python\n# Commentaire Python\n## Faux titre dans code\nprint('ok')\n```\n\n"
            "| Piece | Cote | Couple |\n| :--- | :--- | :--- |\n"
            + "\n".join(f"| Vis_{k} | {10 + k} mm | {20 + k} Nm |" for k in range(1, 45))
        )
        doc_orig = "# Dossier Test\n\n" + "\n\n".join(sections)
        edited_sections = list(sections)
        edited_sections[0] = edited_sections[0] + "\nAjout ligne test L80 masse 3.84 kg."
        doc_edited = "# Dossier Test\n\n" + "\n\n".join(edited_sections)

        def _hashes(chunks: list[dict]) -> list[str]:
            return [hashlib.sha256(c["content"].encode("utf-8")).hexdigest() for c in chunks]

        fixed_a = _hashes(chunking_by_token_size(tok, doc_orig, None, False, 150, 1200))
        fixed_b = _hashes(chunking_by_token_size(tok, doc_edited, None, False, 150, 1200))
        anch_a = _hashes(rag_chunking.chunking_markdown_anchored(tok, doc_orig, None, False, 150, 1200))
        anch_b = _hashes(rag_chunking.chunking_markdown_anchored(tok, doc_edited, None, False, 150, 1200))

        reused_fixed = len(set(fixed_a) & set(fixed_b)) / max(1, len(fixed_b))
        reused_anch = len(set(anch_a) & set(anch_b)) / max(1, len(anch_b))
        self.assertGreater(reused_anch, 0.75)
        self.assertGreater(reused_anch, reused_fixed)

        # Verifie que le faux titre dans ```python``` n'a pas cree de chunk separe
        raw_anch = rag_chunking.chunking_markdown_anchored(tok, doc_orig, None, False, 150, 1200)
        self.assertFalse(any(c["content"].lstrip().startswith("## Faux titre dans code") for c in raw_anch))

        # Verifie repetition de l'en-tete sur tableau decoupe sous petit budget tokens
        big_tbl = (
            "## Table BOM\n\n| Ref | Spec | Masse |\n| :--- | :--- | :--- |\n"
            + "\n".join(f"| 91292A{100 + k} | Vis M4x{10 + k} inox 316 | {k}.2 g |" for k in range(1, 45))
        )
        tbl_chunks = rag_chunking.chunking_markdown_anchored(tok, big_tbl, None, False, 50, 260)
        self.assertGreaterEqual(len(tbl_chunks), 2)
        for tc in tbl_chunks:
            self.assertIn("| Ref | Spec | Masse |", tc["content"])

    def test_virtual_sections_normalized_sha_and_exclusions(self) -> None:
        import rag_chunking  # noqa: E402

        md_v1 = (
            "# Dossier Torse\n\n> Resume executif D-Bot.\n\n"
            "## 📑 Sommaire\n\n- [1. Chassis](#1-chassis)\n- [2. Actionneurs](#2-actionneurs)\n\n---\n\n"
            "## 1. Chassis\nPoutre 7075-T6 epaisseur 8 mm.\n\n"
            "## 2. Actionneurs\nMoteur RS-04 couple 40 Nm.\n\n"
            "## 3. Capteurs\nIMU BNO085 et OAK-D Pro.\n"
        )
        md_toc_edited = (
            "# Dossier Torse\r\n\r\n> Resume executif D-Bot.   \r\n\r\n"
            "## 📑 Sommaire\r\n\r\n- [1. Chassis](#1-chassis)\r\n- [2. Actionneurs](#2-actionneurs)\r\n- [3. Capteurs](#3-capteurs)\r\n\r\n---\r\n\r\n"
            "## 1. Chassis\r\nPoutre 7075-T6 epaisseur 8 mm.\r\n\r\n"
            "## 2. Actionneurs\r\nMoteur RS-04 couple 40 Nm.\r\n\r\n"
            "## 3. Capteurs\r\nIMU BNO085 et OAK-D Pro.\r\n"
        )
        self.assertEqual(
            rag_chunking.compute_normalized_sha256(md_v1, ext=".md"),
            rag_chunking.compute_normalized_sha256(md_toc_edited, ext=".md"),
        )

        secs_v1 = rag_chunking.split_markdown_into_virtual_sections(
            md_v1, "01_Mecanique/DOSSIER_Torse.md", min_bytes=100, min_h2=3
        )
        self.assertIsNotNone(secs_v1)
        # Sommaire doit etre filtre ; intro + 3 sections H2 = 4 sections virtuelles
        self.assertEqual([s["section_key"] for s in secs_v1], ["intro", "1-chassis", "2-actionneurs", "3-capteurs"])

        md_sec2_edit = md_v1.replace("couple 40 Nm", "couple 45 Nm")
        secs_v2 = rag_chunking.split_markdown_into_virtual_sections(
            md_sec2_edit, "01_Mecanique/DOSSIER_Torse.md", min_bytes=100, min_h2=3
        )
        self.assertIsNotNone(secs_v2)
        self.assertEqual(secs_v1[0]["doc_id"], secs_v2[0]["doc_id"])
        self.assertEqual(secs_v1[1]["doc_id"], secs_v2[1]["doc_id"])
        self.assertNotEqual(secs_v1[2]["doc_id"], secs_v2[2]["doc_id"])
        self.assertEqual(secs_v1[3]["doc_id"], secs_v2[3]["doc_id"])

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            for rel in (
                "Code/rag/index_docs.py",
                "Code/rag/README.md",
                "Code/scripts/motors/test_neck.py",
                "Code/tests/test_smoke.py",
                "Code/dbot/motors/neck.py",
            ):
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("ok", encoding="utf-8")
            empty_init = root / "Code/dbot/audio/__init__.py"
            empty_init.parent.mkdir(parents=True, exist_ok=True)
            empty_init.write_text("", encoding="utf-8")
            ws_only = root / "Code/dbot/motors/arm.py"
            ws_only.write_text("   \n\n  \n", encoding="utf-8")
            collected = {str(p.relative_to(root)) for p in rag_chunking.collect_docs_files(root)}
            self.assertEqual(collected, {"Code/rag/README.md", "Code/dbot/motors/neck.py"})

    async def test_index_docs_section_diff_summary_deterministic_and_batch_e2e(self) -> None:
        import numpy as np  # noqa: E402
        from lightrag.utils import EmbeddingFunc  # noqa: E402
        import rag_chunking  # noqa: E402

        async def _fake_embed(texts: list[str]) -> np.ndarray:
            vecs = []
            for txt in texts:
                h = sum(ord(c) for c in txt) % 997
                vecs.append([float((h + j) % 89) / 89.0 + 0.01 for j in range(8)])
            return np.array(vecs, dtype=np.float32)

        llm_calls: list[str] = []
        summary_llm_calls: list[str] = []

        async def _fake_ollama_llm(prompt, system_prompt=None, history_messages=[], **kwargs):
            if rag_chunking.is_entity_summary_prompt(prompt, history_messages):
                summary_llm_calls.append("SUMMARY")
                return "Resume LLM non attendu en mode deterministe."
            llm_calls.append(str(prompt)[:80])
            if "high_level_keywords" in prompt:
                return '{"high_level_keywords": ["Torse"], "low_level_keywords": ["RS-04"]}'
            return (
                "entity<|#|>D-Bot<|#|>System<|#|>Robot humanoide bipede.\n"
                "entity<|#|>RS-04<|#|>Actuator<|#|>Moteur QDD epaule 48 V.\n"
                "relation<|#|>D-Bot<|#|>RS-04<|#|>utilise<|#|>D-Bot integre RS-04.\n"
                "<|COMPLETE|>"
            )

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            docs_dir = root / "docs"
            db_dir = root / "db"
            docs_dir.mkdir()
            db_dir.mkdir()

            big_doc = docs_dir / "DOSSIER_Torse.md"
            base_md = (
                "# Dossier Torse\n\n"
                "## 📑 Sommaire\n\n- [1. Structure](#1-structure)\n- [2. Moteurs](#2-moteurs)\n- [3. Capteurs](#3-capteurs)\n\n"
                "## 1. Structure\nChassis usine en alliage aluminium 7075-T6 epaisseur 8 mm.\n\n"
                "## 2. Moteurs\nActionneurs RS-04 et RS-06 alimentes en 48 V sur bus CAN-FD.\n\n"
                "## 3. Capteurs\nCentrale IMU BNO085 et camera OAK-D Pro.\n"
            )
            big_doc.write_text(base_md, encoding="utf-8")
            (docs_dir / "note_a.md").write_text("# Note A\nVis 91292A118 M4x16.", encoding="utf-8")
            (docs_dir / "note_b.md").write_text("# Note B\nRoulement RB8016.", encoding="utf-8")

            args = index_docs.parse_cli_args(
                ["--provider", "ollama", "--summary-mode", "deterministic", "--batch-size", "4"]
            )
            fake_emb = EmbeddingFunc(embedding_dim=8, max_token_size=8192, func=_fake_embed)
            with patch.object(index_docs, "DOCS_ROOT", docs_dir), patch.object(
                index_docs, "DB_PATH", db_dir
            ), patch.object(index_docs, "INDEX_LOG", db_dir / "indexed_files.json"), patch.object(
                index_docs, "embedding_func", fake_emb
            ), patch.object(
                index_docs, "ManagedOllamaServer", _DummyManagedOllama
            ), patch.object(
                index_docs, "_ensure_ollama_available", return_value=(True, "OK")
            ), patch.object(
                index_docs, "get_llm_func", AsyncMock(return_value=_fake_ollama_llm)
            ), patch.object(
                rag_chunking, "SECTION_SPLIT_MIN_BYTES", 120
            ):
                await index_docs.run_indexing(args)

                idx_data = json.loads((db_dir / "indexed_files.json").read_text(encoding="utf-8"))
                self.assertEqual(len(idx_data), 3)
                self.assertIn("sections", idx_data[str(big_doc.resolve())])
                self.assertEqual(len(idx_data[str(big_doc.resolve())]["sections"]), 3)
                self.assertEqual(summary_llm_calls, [])

                calls_after_init = len(llm_calls)
                # 1) Modification purement cosmetique (Sommaire + espaces + bump mtime) -> 0 appel LLM
                toc_only_md = base_md.replace(
                    "- [3. Capteurs](#3-capteurs)",
                    "- [3. Capteurs](#3-capteurs)\n- [Note](#note)",
                ) + "   \n\n"
                big_doc.write_text(toc_only_md, encoding="utf-8")
                future_ts = big_doc.stat().st_mtime + 10
                os.utime(big_doc, (future_ts, future_ts))

                await index_docs.run_indexing(args)
                self.assertEqual(len(llm_calls), calls_after_init)

                # 2) Edition reelle dans UNE seule section (2. Moteurs) -> seule cette section rappelle le LLM
                sec2_edited = toc_only_md.replace("48 V sur bus CAN-FD", "50.4 V sur bus CAN-FD 5 Mbps")
                big_doc.write_text(sec2_edited, encoding="utf-8")
                future_ts2 = big_doc.stat().st_mtime + 20
                os.utime(big_doc, (future_ts2, future_ts2))

                ds_before = json.loads((db_dir / "kv_store_doc_status.json").read_text(encoding="utf-8"))
                sec1_id = idx_data[str(big_doc.resolve())]["sections"]["1-structure"]["doc_id"]
                sec3_id = idx_data[str(big_doc.resolve())]["sections"]["3-capteurs"]["doc_id"]
                sec2_old_id = idx_data[str(big_doc.resolve())]["sections"]["2-moteurs"]["doc_id"]

                await index_docs.run_indexing(args)
                # 1 seul chunk (gleaning=1 => 2 appels LLM) et 0 appel summary LLM
                self.assertGreater(len(llm_calls), calls_after_init)
                self.assertLessEqual(len(llm_calls) - calls_after_init, 3)
                self.assertEqual(summary_llm_calls, [])

                ds_after = json.loads((db_dir / "kv_store_doc_status.json").read_text(encoding="utf-8"))
                self.assertIn(sec1_id, ds_after)
                self.assertIn(sec3_id, ds_after)
                self.assertNotIn(sec2_old_id, ds_after)
                self.assertEqual(ds_after[sec1_id]["updated_at"], ds_before[sec1_id]["updated_at"])

    async def test_agent_indexing_section_diff_prepare_and_commit(self) -> None:
        import numpy as np  # noqa: E402
        from lightrag import LightRAG  # noqa: E402
        from lightrag.utils import EmbeddingFunc  # noqa: E402
        import agent_indexing  # noqa: E402
        import rag_chunking  # noqa: E402

        async def _fake_embed(texts: list[str]) -> np.ndarray:
            return np.array(
                [[float((sum(ord(c) for c in t) + j) % 89) / 89.0 + 0.01 for j in range(8)] for t in texts],
                dtype=np.float32,
            )

        async def _bomb_llm(*a, **k):
            raise AssertionError("Aucun LLM ne doit etre appele pendant commit_agent_bundle !")

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            docs_dir = root / "docs"
            db_dir = root / "db"
            docs_dir.mkdir()
            db_dir.mkdir()

            big_doc = docs_dir / "DOSSIER_Bassin.md"
            md_v1 = (
                "# Bassin\n\n"
                "## 1. Pont\nPont de hanches en alu 7075-T6.\n\n"
                "## 2. Waist\nRoulement RB8016 sur axe RS-06.\n\n"
                "## 3. Batteries\nPacks 13S 48 V hot-swap.\n"
            )
            big_doc.write_text(md_v1, encoding="utf-8")

            rag_real = LightRAG(
                working_dir=str(db_dir),
                llm_model_func=_bomb_llm,
                embedding_func=EmbeddingFunc(embedding_dim=8, max_token_size=8192, func=_fake_embed),
                chunking_func=rag_chunking.chunking_markdown_anchored,
                chunk_token_size=1600,
                chunk_overlap_token_size=150,
                llm_model_max_async=1,
                addon_params={"language": "French"},
            )
            await rag_real.initialize_storages()

            with patch.object(rag_chunking, "SECTION_SPLIT_MIN_BYTES", 80):
                prep1 = agent_indexing.prepare_agent_bundle(
                    docs_root=docs_dir, db_path=db_dir, effort_profile="balanced"
                )
                self.assertEqual(len(prep1["manifest"]["chunks"]), 3)
                exts1 = {
                    ch["chunk_hash"]: (
                        f"entity<|#|>Ent_{idx}<|#|>Component<|#|>Description section {ch.get('section_key')}.\n"
                        "<|COMPLETE|>"
                    )
                    for idx, ch in enumerate(prep1["manifest"]["chunks"])
                }
                res1 = await agent_indexing.commit_agent_bundle(
                    rag=rag_real,
                    db_path=db_dir,
                    job_id_or_path=prep1["job_id"],
                    extractions={"chunk_extractions": exts1},
                )
                self.assertEqual(len(res1["committed"]), 3)

                # Modifie uniquement la section 2 -> prepare ne doit retourner qu'1 seul chunk !
                big_doc.write_text(md_v1.replace("RS-06", "RS-06 couple 36 Nm"), encoding="utf-8")
                future_ts = big_doc.stat().st_mtime + 10
                os.utime(big_doc, (future_ts, future_ts))

                prep2 = agent_indexing.prepare_agent_bundle(
                    docs_root=docs_dir, db_path=db_dir, effort_profile="balanced"
                )
                self.assertEqual(len(prep2["manifest"]["documents"]), 1)
                self.assertEqual(prep2["manifest"]["documents"][0]["section_key"], "2-waist")
                self.assertEqual(len(prep2["manifest"]["chunks"]), 1)

                ch2 = prep2["manifest"]["chunks"][0]
                res2 = await agent_indexing.commit_agent_bundle(
                    rag=rag_real,
                    db_path=db_dir,
                    job_id_or_path=prep2["job_id"],
                    extractions={
                        "chunk_extractions": {
                            ch2["chunk_hash"]: "entity<|#|>RS-06<|#|>Hardware<|#|>Couple 36 Nm.\n<|COMPLETE|>"
                        }
                    },
                )
                self.assertEqual(len(res2["committed"]), 1)
                idx_after = json.loads((db_dir / "indexed_files.json").read_text(encoding="utf-8"))
                self.assertEqual(len(idx_after[str(big_doc.resolve())]["sections"]), 3)

    def test_resolve_default_db_path_and_mirror_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            local_db = tmp_path / "local_db"
            drive_db = tmp_path / "drive_db"
            drive_db.mkdir()
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("RAG_DB_PATH", None)
                with patch.object(rag_runtime, "DEFAULT_LOCAL_DB_PATH", str(local_db)), patch.object(
                    rag_runtime, "DEFAULT_DRIVE_MIRROR_DB_PATH", str(drive_db)
                ):
                    self.assertEqual(rag_runtime.resolve_default_db_path(), str(drive_db))
                    local_db.mkdir()
                    self.assertEqual(rag_runtime.resolve_default_db_path(), str(local_db))

                with patch.dict(os.environ, {"RAG_DB_PATH": "/custom/db"}, clear=False):
                    self.assertEqual(rag_runtime.resolve_default_db_path(), "/custom/db")

            # Garde-fou : ne jamais copier un repertoire /tmp ou /var/folders vers Google Drive
            ok_tmp, msg_tmp = rag_runtime.sync_db_to_backup_mirror(local_db, drive_db)
            self.assertFalse(ok_tmp)
            self.assertIn("sandbox", msg_tmp.lower())

            ok_same, msg_same = rag_runtime.sync_db_to_backup_mirror(Path("/opt/fake_db"), Path("/opt/fake_db"))
            self.assertFalse(ok_same)

    async def test_adaptive_gleaning_policy_and_bucket_execution(self) -> None:
        import numpy as np  # noqa: E402
        from lightrag.utils import EmbeddingFunc  # noqa: E402
        import rag_chunking  # noqa: E402

        self.assertEqual(rag_chunking.resolve_gleaning_for_doc("00_Architecture/FINAL_Torse.md", "adaptive"), 1)
        self.assertEqual(rag_chunking.resolve_gleaning_for_doc("01_Meca/DOSSIER_TECHNIQUE_Bassin.md", "adaptive"), 1)
        self.assertEqual(rag_chunking.resolve_gleaning_for_doc("01_Meca/SYNTHESE_METROLOGIQUE_Torse.md", "adaptive"), 1)
        self.assertEqual(rag_chunking.resolve_gleaning_for_doc("Manuels/RS06.pdf", "adaptive"), 1)
        self.assertEqual(rag_chunking.resolve_gleaning_for_doc("01_Meca/media/schema.svg", "adaptive"), 1)
        self.assertEqual(rag_chunking.resolve_gleaning_for_doc(".agents/AGENTS.md", "adaptive"), 0)
        self.assertEqual(rag_chunking.resolve_gleaning_for_doc("Code/scripts/motors/ota_update.py", "adaptive"), 0)
        self.assertEqual(rag_chunking.resolve_gleaning_for_doc(".agents/AGENTS.md", "on"), 1)
        self.assertEqual(rag_chunking.resolve_gleaning_for_doc("00_Architecture/FINAL_Torse.md", "off"), 0)

        async def _fake_embed(texts: list[str]) -> np.ndarray:
            return np.array(
                [[float((sum(ord(c) for c in t) + j) % 89) / 89.0 + 0.01 for j in range(8)] for t in texts],
                dtype=np.float32,
            )

        calls_by_doc = {"crit": 0, "std": 0}

        async def _fake_ollama_llm(prompt, system_prompt=None, history_messages=[], **kwargs):
            if rag_chunking.is_entity_summary_prompt(prompt, history_messages):
                return "Resume deterministe attendu."
            joined = str(prompt or "") + "\n" + "\n".join(str(m.get("content", "")) for m in (history_messages or []))
            if "Couple 40 Nm RS-04" in joined:
                calls_by_doc["crit"] += 1
                return (
                    "entity<|#|>RS-04<|#|>Actuator<|#|>Couple 40 Nm.\n"
                    "entity<|#|>D-Bot<|#|>System<|#|>Robot.\n"
                    "relation<|#|>D-Bot<|#|>RS-04<|#|>integre<|#|>Bride epaule RS-04.\n"
                    "<|COMPLETE|>"
                )
            if "Configuration bus CAN" in joined:
                calls_by_doc["std"] += 1
                return (
                    "entity<|#|>Bus CAN<|#|>Bus<|#|>Configuration bus CAN.\n"
                    "entity<|#|>D-Bot<|#|>System<|#|>Robot.\n"
                    "relation<|#|>D-Bot<|#|>Bus CAN<|#|>utilise<|#|>Communication.\n"
                    "<|COMPLETE|>"
                )
            return "<|COMPLETE|>"

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            docs_dir = root / "docs"
            db_dir = root / "db"
            docs_dir.mkdir()
            db_dir.mkdir()
            (docs_dir / "FINAL_Critique.md").write_text("# Critique\nCouple 40 Nm RS-04.", encoding="utf-8")
            (docs_dir / "note_standard.md").write_text("# Standard\nConfiguration bus CAN.", encoding="utf-8")

            args = index_docs.parse_cli_args(
                ["--provider", "ollama", "--summary-mode", "deterministic", "--gleaning-mode", "adaptive", "--batch-size", "4"]
            )
            fake_emb = EmbeddingFunc(embedding_dim=8, max_token_size=8192, func=_fake_embed)
            with patch.object(index_docs, "DOCS_ROOT", docs_dir), patch.object(
                index_docs, "DB_PATH", db_dir
            ), patch.object(index_docs, "INDEX_LOG", db_dir / "indexed_files.json"), patch.object(
                index_docs, "embedding_func", fake_emb
            ), patch.object(
                index_docs, "ManagedOllamaServer", _DummyManagedOllama
            ), patch.object(
                index_docs, "_ensure_ollama_available", return_value=(True, "OK")
            ), patch.object(
                index_docs, "get_llm_func", AsyncMock(return_value=_fake_ollama_llm)
            ):
                await index_docs.run_indexing(args)

        # Critique: extract + 1 gleaning = 2 appels ; Standard: extract sans gleaning = 1 appel
        self.assertEqual(calls_by_doc["crit"], 2)
        self.assertEqual(calls_by_doc["std"], 1)

    def test_sanitize_extraction_and_running_in_tests_detection(self) -> None:
        import rag_chunking  # noqa: E402

        # 1. Trailing <|#|>, entity# prefix typo, glued records and glued <|COMPLETE|>
        dirty = (
            "entity<|#|>D-Bot<|#|>Other<|#|>Robot.<|#|>"
            "entity#Moteur Xiaomi<|#|>Artifact<|#|>Moteur CAN.<|#|>\n"
            "relation<|#|>D-Bot<|#|>Moteur Xiaomi<|#|>utilise<|#|>Entrainement.<|#|><|COMPLETE|>"
        )
        cleaned = rag_chunking.sanitize_lightrag_extraction_output(dirty)
        lines = cleaned.splitlines()
        self.assertEqual(
            lines,
            [
                "entity<|#|>D-Bot<|#|>Other<|#|>Robot.",
                "entity<|#|>Moteur Xiaomi<|#|>Artifact<|#|>Moteur CAN.",
                "relation<|#|>D-Bot<|#|>Moteur Xiaomi<|#|>utilise<|#|>Entrainement.",
                "<|COMPLETE|>",
            ],
        )
        # Non-extraction strings (JSON, summaries) remain untouched
        plain_json = '{"high_level_keywords": ["RS-06"], "low_level_keywords": ["RB8016"]}'
        self.assertEqual(rag_chunking.sanitize_lightrag_extraction_output(plain_json), plain_json)

        # 2. Production invocation detection must NOT rely on "unittest" in sys.modules
        self.assertFalse(index_docs._detect_running_in_tests(["/path/Code/rag/index_docs.py", "--update"]))
        self.assertTrue(index_docs._detect_running_in_tests(["/opt/lib/unittest/__main__.py", "test_rag_resilience"]))
        self.assertTrue(index_docs._detect_running_in_tests(["/opt/bin/pytest", "-q"]))

    async def test_forced_files_reindex_purges_llm_cache_and_calls_llm_freshly(self) -> None:
        import numpy as np  # noqa: E402
        from lightrag.utils import EmbeddingFunc  # noqa: E402
        import rag_chunking  # noqa: E402

        self.assertFalse(index_docs.parse_cli_args([]).no_cache)
        self.assertTrue(index_docs.parse_cli_args(["--no-cache"]).no_cache)

        async def _fake_embed(texts: list[str]) -> np.ndarray:
            return np.array(
                [[float((sum(ord(c) for c in t) + j) % 89) / 89.0 + 0.01 for j in range(8)] for t in texts],
                dtype=np.float32,
            )

        state = {"version": "v1", "std_calls": 0, "sec_calls": 0}

        async def _fake_llm(prompt, system_prompt=None, history_messages=[], **kwargs):
            if rag_chunking.is_entity_summary_prompt(prompt, history_messages):
                return "Resume deterministe attendu."
            joined = str(prompt or "") + "\n" + "\n".join(str(m.get("content", "")) for m in (history_messages or []))
            if "Contenu standard RS-06" in joined:
                state["std_calls"] += 1
                ver = state["version"]
                return (
                    f"entity<|#|>RS-06 {ver}<|#|>Actuator<|#|>Actionneur {ver}.\n"
                    f"entity<|#|>D-Bot<|#|>System<|#|>Robot {ver}.\n"
                    f"relation<|#|>D-Bot<|#|>RS-06 {ver}<|#|>integre<|#|>Lien {ver}.\n"
                    "<|COMPLETE|>"
                )
            if "DOSSIER_Sections_Cache.md" in joined or "Section test" in joined:
                state["sec_calls"] += 1
                ver = state["version"]
                return (
                    f"entity<|#|>Module_{state['sec_calls']}_{ver}<|#|>Component<|#|>Section {ver}.\n"
                    "<|COMPLETE|>"
                )
            return "<|COMPLETE|>"

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            docs_dir = root / "docs"
            db_dir = root / "db"
            docs_dir.mkdir()
            db_dir.mkdir()

            doc_file = docs_dir / "doc_cache_test.md"
            doc_file.write_text("# Test Cache\nContenu standard RS-06.", encoding="utf-8")

            big_doc = docs_dir / "DOSSIER_Sections_Cache.md"
            big_doc.write_text(
                "# Gros Dossier\n\n"
                "## 1. Pont\nSection test pont aluminium.\n\n"
                "## 2. Waist\nSection test waist RB8016.\n\n"
                "## 3. Batteries\nSection test batteries 48V.\n",
                encoding="utf-8",
            )

            fake_emb = EmbeddingFunc(embedding_dim=8, max_token_size=8192, func=_fake_embed)
            with patch.object(index_docs, "DOCS_ROOT", docs_dir), patch.object(
                index_docs, "DB_PATH", db_dir
            ), patch.object(index_docs, "INDEX_LOG", db_dir / "indexed_files.json"), patch.object(
                index_docs, "embedding_func", fake_emb
            ), patch.object(
                index_docs, "ManagedOllamaServer", _DummyManagedOllama
            ), patch.object(
                index_docs, "_ensure_ollama_available", return_value=(True, "OK")
            ), patch.object(
                index_docs, "get_llm_func", AsyncMock(return_value=_fake_llm)
            ):
                # 1. Indexation initiale du document standard -> 1 appel LLM et trace cache presente
                args_std = index_docs.parse_cli_args(
                    ["--provider", "ollama", "--summary-mode", "deterministic", "--gleaning-mode", "off", "--files", str(doc_file)]
                )
                await index_docs.run_indexing(args_std)
                self.assertEqual(state["std_calls"], 1)

                cache_1 = json.loads((db_dir / "kv_store_llm_response_cache.json").read_text(encoding="utf-8"))
                chunks_1 = json.loads((db_dir / "kv_store_text_chunks.json").read_text(encoding="utf-8"))
                self.assertTrue(any("RS-06 v1" in str(v.get("return", "")) for v in cache_1.values() if isinstance(v, dict)))
                std_chunks_1 = [
                    c for c in chunks_1.values()
                    if isinstance(c, dict) and "Contenu standard RS-06" in str(c.get("content", ""))
                ]
                self.assertEqual(len(std_chunks_1), 1)
                self.assertTrue(bool(std_chunks_1[0].get("llm_cache_list")))

                # 2. Re-indexation forcee via --files SANS modifier doc_file -> purge cache + appel frais v2
                state["version"] = "v2"
                await index_docs.run_indexing(args_std)
                self.assertEqual(state["std_calls"], 2)

                cache_2 = json.loads((db_dir / "kv_store_llm_response_cache.json").read_text(encoding="utf-8"))
                chunks_2 = json.loads((db_dir / "kv_store_text_chunks.json").read_text(encoding="utf-8"))
                full_ents_2 = json.loads((db_dir / "kv_store_full_entities.json").read_text(encoding="utf-8"))
                cache_returns_2 = [str(v.get("return", "")) for v in cache_2.values() if isinstance(v, dict)]
                self.assertTrue(any("RS-06 v2" in txt for txt in cache_returns_2))
                self.assertFalse(any("RS-06 v1" in txt for txt in cache_returns_2))
                self.assertTrue(
                    any("RS-06 v2" in str(v.get("entity_names", [])) for v in full_ents_2.values() if isinstance(v, dict))
                )
                std_chunks_2 = [
                    c for c in chunks_2.values()
                    if isinstance(c, dict) and "Contenu standard RS-06" in str(c.get("content", ""))
                ]
                self.assertEqual(len(std_chunks_2), 1)
                self.assertTrue(bool(std_chunks_2[0].get("llm_cache_list")))

                # 3. Gros .md sectionne : --files ne doit pas sauter silencieusement les sections
                with patch.object(rag_chunking, "SECTION_SPLIT_MIN_BYTES", 80):
                    args_sec = index_docs.parse_cli_args(
                        ["--provider", "ollama", "--summary-mode", "deterministic", "--gleaning-mode", "off", "--files", str(big_doc)]
                    )
                    await index_docs.run_indexing(args_sec)
                    self.assertEqual(state["sec_calls"], 3)

                    await index_docs.run_indexing(args_sec)
                    self.assertEqual(state["sec_calls"], 6)


class _DummyManagedOllama:
    def __init__(self, base_url=None, model=None) -> None:
        self.base_url = base_url or "http://127.0.0.1:11434"
        self.model = model or "qwen3.8:27b-mlx"

    def ensure_started(self, timeout_s: float = 15.0) -> bool:
        return True

    def cleanup(self, force_unload_external: bool = False) -> None:
        return None


if __name__ == "__main__":
    unittest.main()
