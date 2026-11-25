#!/opt/homebrew/bin/python3.11
"""Tests unitaires et API FastAPI pour les extensions D-Bot RAG Studio."""

from __future__ import annotations

import fcntl
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

_RAG_DIR = str(Path(__file__).resolve().parent)
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

import rag_monitor_ui  # noqa: E402
import rag_studio_service  # noqa: E402


_PNG_1X1_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0"
    b"\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _seed_studio_workspace(tmp_dir: Path) -> tuple[Path, Path, Path, Path, Path, Path]:
    docs_root = tmp_dir / "docs"
    db_path = tmp_dir / "db"
    snaps_root = tmp_dir / "Visual_Snapshots"
    docs_root.mkdir(parents=True)
    db_path.mkdir(parents=True)
    (snaps_root / "Vues_Ensemble").mkdir(parents=True)
    (snaps_root / "Pieces_Isolees" / "Selle_Pont").mkdir(parents=True)

    (snaps_root / "Vues_Ensemble" / "01_vue_face.png").write_bytes(_PNG_1X1_BYTES)
    (snaps_root / "Pieces_Isolees" / "Selle_Pont" / "Selle_Pont_iso.png").write_bytes(
        _PNG_1X1_BYTES
    )

    rel_doc = "01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Test.md"
    (docs_root / rel_doc).parent.mkdir(parents=True)
    (docs_root / rel_doc).write_text(
        "# Dossier Test\nVis CHC M4x16 McMaster 91292A118, roulement RB8016, +/- 0.02 deg.\n",
        encoding="utf-8",
    )

    audit_json_rel = "01_Mecanique_et_Chassis/Torse_et_Bassin/Audits/AUDIT_METROLOGIQUE_Torse_et_Bassin.json"
    (docs_root / audit_json_rel).parent.mkdir(parents=True, exist_ok=True)
    (docs_root / audit_json_rel).write_text(
        json.dumps(
            {
                "document_name": "Torse-123 v42",
                "assembly_summary": {"total_mass_kg": 18.4},
                "components": [{"name": "Selle_Pont", "mass_kg": 0.42, "bbox_mm": [140, 145, 22]}],
            }
        ),
        encoding="utf-8",
    )

    (db_path / "kv_store_doc_status.json").write_text("{}", encoding="utf-8")
    (db_path / "kv_store_full_docs.json").write_text("{}", encoding="utf-8")
    (db_path / "kv_store_text_chunks.json").write_text("{}", encoding="utf-8")
    (db_path / "kv_store_llm_response_cache.json").write_text("{}", encoding="utf-8")
    (db_path / "vdb_chunks.json").write_text(json.dumps({"data": []}), encoding="utf-8")
    (db_path / "graph_chunk_entity_relation.graphml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n'
        '  <graph edgedefault="undirected">\n'
        '    <node id="RB8016"><data key="description">Roulement croise bassin</data></node>\n'
        '    <node id="91292A118"><data key="description">Vis CHC M4x16 inox</data></node>\n'
        '    <edge source="RB8016" target="91292A118"><data key="description">Fixation</data></edge>\n'
        "  </graph>\n"
        "</graphml>\n",
        encoding="utf-8",
    )

    log_path = tmp_dir / "rag_indexing.log"
    log_path.write_text("", encoding="utf-8")
    bench_path = tmp_dir / "BENCHMARK_QA_DBOT_120.json"
    bench_path.write_text(
        json.dumps(
            {
                "benchmark_name": "Test Bench",
                "audit_seeds": [
                    {
                        "seed_id": "S1",
                        "section": "Mecanique",
                        "question": "Quel roulement est monte au bassin ?",
                        "answer": "RB8016",
                    }
                ],
                "data_recipes_qa": [
                    {
                        "id": "Q1",
                        "category": "BOM",
                        "source_doc": rel_doc,
                        "question": "Reference vis M4x16 ?",
                        "answer": "91292A118",
                        "numeric_token": "91292A118",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    audit_md_path = tmp_dir / "AUDIT_INTEGRITE.md"
    audit_md_path.write_text("# Audit Test\n", encoding="utf-8")
    return docs_root, db_path, log_path, bench_path, audit_md_path, snaps_root


class StudioServiceUnitTests(unittest.TestCase):
    def test_extract_mcmaster_and_latex_check(self) -> None:
        sample = "Utiliser 91292A118 avec ecrou 93625A150 et 91292A118 (+/- 0.02 deg)."
        self.assertEqual(rag_studio_service.extract_mcmaster_refs(sample), ["91292A118", "93625A150"])
        self.assertFalse(rag_studio_service.has_dollar_or_latex(sample))
        self.assertTrue(rag_studio_service.has_dollar_or_latex("Valeur " + chr(36) + "x" + chr(36)))
        self.assertTrue(rag_studio_service.has_dollar_or_latex(r"Angle \approx 20 deg"))

    def test_think_splitter_partial_tags(self) -> None:
        sp = rag_studio_service._ThinkSplitter()
        out = []
        for tok in ["<thi", "nk>Etape", " 1</th", "ink>Reponse", " finale"]:
            out.extend(sp.feed(tok))
        out.extend(sp.flush())
        th = "".join(v for k, v in out if k == "thinking")
        ans = "".join(v for k, v in out if k == "token")
        self.assertEqual(th, "Etape 1")
        self.assertEqual(ans, "Reponse finale")

    def test_resolve_profile_ssrf_and_snapshot_traversal(self) -> None:
        g4 = rag_studio_service.resolve_profile_target("ollama_gemma4")
        self.assertEqual(g4["backend"], "ollama")
        un = rag_studio_service.resolve_profile_target("unsloth_qwen38")
        self.assertEqual(un["backend"], "openai_compat")
        with self.assertRaises(ValueError):
            rag_studio_service.resolve_profile_target(
                "custom_openai", custom_url="https://evil.example.com/v1", custom_model="x"
            )
        ok_custom = rag_studio_service.resolve_profile_target(
            "custom_openai", custom_url="http://127.0.0.1:8090/v1", custom_model="local-qwen"
        )
        self.assertEqual(ok_custom["model"], "local-qwen")

        with tempfile.TemporaryDirectory() as td:
            _, _, _, _, _, snaps_root = _seed_studio_workspace(Path(td))
            listed = rag_studio_service.list_visual_snapshots(snaps_root)
            self.assertEqual(listed["total"], 2)
            with self.assertRaises(ValueError):
                rag_studio_service.resolve_snapshot_path("../outside.png", snapshots_root=snaps_root)


class StudioApiIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._root = Path(self._tmp.name)
        docs_root, db_path, log_path, bench_path, audit_md_path, snaps_root = _seed_studio_workspace(
            self._root
        )
        self.db_path = db_path
        self.app = rag_monitor_ui.create_app(
            db_path=db_path,
            docs_root=docs_root,
            log_path=log_path,
            benchmark_path=bench_path,
            audit_md_path=audit_md_path,
            snapshots_root=snaps_root,
            cache_ttl_s=60.0,
        )
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_dashboard_html_zero_dollar_and_studio_elements(self) -> None:
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        html = resp.text
        self.assertNotIn(chr(36), html)
        for dom_id in [
            "ollama-pill",
            "unsloth-pill",
            "searxng-pill",
            "btn-toggle-searxng",
            "ram-pill",
            "tab-chat",
            "chat-use-web",
            "tab-vision",
            "arena-results",
            "cad-diag-modal",
            "minmax(0, 2.2fr)",
            "max-width:none",
            "overflow-wrap:anywhere",
        ]:
            self.assertIn(dom_id, html)

        script_match = re.search(r"<script>(.*)</script>", html, re.DOTALL)
        self.assertIsNotNone(script_match)
        node_bin = shutil.which("node")
        if node_bin and script_match is not None:
            with tempfile.NamedTemporaryFile(
                "w", suffix=".js", encoding="utf-8", delete=False
            ) as tmp_js:
                tmp_js.write(script_match.group(1))
                tmp_js_path = Path(tmp_js.name)
            try:
                proc = subprocess.run(
                    [node_bin, "--check", str(tmp_js_path)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            finally:
                tmp_js_path.unlink(missing_ok=True)

    def test_engines_status_and_unload_guard(self) -> None:
        fake_mem = {"available": True, "total_gb": 64.0, "used_gb": 22.0, "free_or_reclaimable_gb": 42.0, "percent_used": 34.4}
        fake_ollama = {"reachable": True, "base_url": "http://127.0.0.1:11434", "installed_models": ["gemma4:26b"], "loaded_models": [{"name": "gemma4:26b", "size_gb": 17.0, "size_vram_gb": 17.0, "expires_at": ""}], "total_vram_gb": 17.0, "gemma4_installed": True, "qwen38_installed": True}
        fake_unsloth = {"reachable": True, "base_url": "http://127.0.0.1:8888/v1", "configured_model": "unsloth/Qwen3.8-27B-GGUF", "loaded_models": ["unsloth/Qwen3.8-27B-GGUF"]}
        with patch.object(rag_studio_service, "get_macos_memory_info", return_value=fake_mem), \
             patch.object(rag_studio_service, "get_ollama_telemetry", return_value=fake_ollama), \
             patch.object(rag_studio_service, "get_unsloth_telemetry", return_value=fake_unsloth):
            r = self.client.get("/api/engines/status")
            self.assertEqual(r.status_code, 200)
            data = r.json()
            self.assertTrue(data["dual_loaded"])
            self.assertTrue(data["ram_warning"])

        with patch.object(rag_monitor_ui, "unload_ollama_models", return_value={"unloaded": ["gemma4:26b"], "errors": []}):
            r2 = self.client.post("/api/engines/ollama/unload", json={})
            self.assertEqual(r2.status_code, 200)
            self.assertEqual(r2.json()["unloaded"], ["gemma4:26b"])

        lock_file = self.db_path / ".indexing.lock"
        with lock_file.open("a+", encoding="utf-8") as fh:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                r_locked = self.client.post("/api/engines/ollama/unload", json={})
                self.assertEqual(r_locked.status_code, 409)
            finally:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)

    def test_chat_stream_sse_file_mode_and_lock_guard(self) -> None:
        lock_file = self.db_path / ".indexing.lock"
        with lock_file.open("a+", encoding="utf-8") as fh:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                r_lock = self.client.post(
                    "/api/chat/stream",
                    json={"query": "Test", "profile": "ollama_gemma4", "context_mode": "none"},
                )
                self.assertEqual(r_lock.status_code, 409)
            finally:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)

        r_trav = self.client.post(
            "/api/chat/stream",
            json={
                "query": "Test",
                "profile": "ollama_gemma4",
                "context_mode": "file",
                "target_rel_path": "../../etc/passwd",
            },
        )
        self.assertEqual(r_trav.status_code, 400)

        def _fake_stream(**kwargs):
            yield {"type": "thinking", "delta": "Verification fichier."}
            yield {"type": "token", "delta": "Utiliser vis 91292A118 sur RB8016."}
            yield {
                "type": "done",
                "answer": "Utiliser vis 91292A118 sur RB8016.",
                "thinking": "Verification fichier.",
                "mcmaster_refs": ["91292A118"],
                "has_dollar_or_latex": False,
                "metrics": {"profile": "ollama_gemma4", "model": "gemma4:26b", "ttft_s": 0.12, "total_s": 0.45, "tok_per_s": 38.5},
            }

        with patch.object(rag_monitor_ui, "stream_llm_chat", side_effect=_fake_stream):
            r_ok = self.client.post(
                "/api/chat/stream",
                json={
                    "query": "Quelle vis ?",
                    "profile": "ollama_gemma4",
                    "context_mode": "file",
                    "target_rel_path": "01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Test.md",
                },
            )
            self.assertEqual(r_ok.status_code, 200)
            body = r_ok.text
            self.assertIn("event: context", body)
            self.assertIn("event: thinking", body)
            self.assertIn("event: done", body)
            self.assertIn("91292A118", body)

    def test_vlm_snapshots_and_analyze(self) -> None:
        r_list = self.client.get("/api/vlm/snapshots")
        self.assertEqual(r_list.status_code, 200)
        self.assertTrue(r_list.json()["available"])
        self.assertEqual(len(r_list.json()["groups"]["Vues_Ensemble"]), 1)

        r_img = self.client.get("/api/vlm/snapshot-image?rel_path=Vues_Ensemble/01_vue_face.png")
        self.assertEqual(r_img.status_code, 200)
        self.assertEqual(r_img.headers["content-type"], "image/png")

        r_bad = self.client.get("/api/vlm/snapshot-image?rel_path=../secret.png")
        self.assertEqual(r_bad.status_code, 400)

        fake_res = {
            "answer": "Silhouette conforme, percages 91292A118 alignes.",
            "thinking": "",
            "mcmaster_refs": ["91292A118"],
            "has_dollar_or_latex": False,
            "metrics": {"model": "gemma4:26b", "ttft_s": 0.2, "total_s": 0.9, "tok_per_s": 32.0},
        }
        with patch.object(rag_monitor_ui, "complete_llm_chat", return_value=fake_res), \
             patch.object(rag_monitor_ui, "build_vlm_cad_context", return_value={"cad_context": "Torse-123 v42", "rag_context": "", "sources": []}):
            r_vlm = self.client.post(
                "/api/vlm/analyze",
                json={
                    "prompt": "Verifier la vue de face",
                    "profile": "ollama_gemma4",
                    "snapshot_rel_path": "Vues_Ensemble/01_vue_face.png",
                    "include_cad_context": True,
                },
            )
            self.assertEqual(r_vlm.status_code, 200)
            self.assertIn("91292A118", r_vlm.json()["mcmaster_refs"])

    def test_cad_diagnose_read_only(self) -> None:
        fake_res = {
            "answer": "```diff\n- version: v41\n+ version: v42\n```",
            "thinking": "",
            "mcmaster_refs": [],
            "has_dollar_or_latex": False,
            "metrics": {"model": "unsloth/Qwen3.8-27B-GGUF", "ttft_s": 0.3, "total_s": 1.1, "tok_per_s": 24.5},
        }
        with patch.object(rag_monitor_ui, "complete_llm_chat", return_value=fake_res):
            r = self.client.post(
                "/api/cad/diagnose",
                json={
                    "mode": "diff",
                    "profile": "unsloth_qwen38",
                    "rel_path": "01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Test.md",
                    "drift_item": {"code": "CAD_VERSION_DRIFT", "message": "v41 vs v42"},
                },
            )
            self.assertEqual(r.status_code, 200)
            self.assertIn("+ version: v42", r.json()["answer"])

    def test_arena_questions_and_sequential_run(self) -> None:
        r_q = self.client.get("/api/arena/questions")
        self.assertEqual(r_q.status_code, 200)
        self.assertEqual(r_q.json()["count"], 2)

        def _fake_complete(**kwargs):
            model = kwargs["target"]["model"]
            return {
                "answer": f"Reponse {model} : reference 91292A118.",
                "thinking": "",
                "mcmaster_refs": ["91292A118"],
                "has_dollar_or_latex": False,
                "metrics": {"profile": kwargs["target"]["profile"], "model": model, "ttft_s": 0.25, "total_s": 0.8, "tok_per_s": 40.0, "completion_tokens": 20},
            }

        with patch.object(rag_studio_service, "complete_llm_chat", side_effect=_fake_complete), \
             patch.object(rag_studio_service, "unload_ollama_models", return_value={"unloaded": ["gemma4:26b"]}) as mock_unload, \
             patch.object(rag_studio_service, "get_macos_memory_info", return_value={"used_gb": 24.0}):
            r_run = self.client.post(
                "/api/arena/run",
                json={
                    "question": "Reference vis M4x16 ?",
                    "targets": [{"profile": "ollama_gemma4"}, {"profile": "unsloth_qwen38"}],
                    "use_rag": False,
                    "unload_ollama_between": True,
                    "expected_token": "91292A118",
                },
            )
            self.assertEqual(r_run.status_code, 200)
            data = r_run.json()
            self.assertEqual(len(data["results"]), 2)
            self.assertTrue(all(x["token_matched"] for x in data["results"]))
            mock_unload.assert_called_once()

        r_bad_custom = self.client.post(
            "/api/arena/run",
            json={
                "question": "Test",
                "targets": [
                    {"profile": "ollama_gemma4"},
                    {"profile": "custom_openai", "custom_url": "https://remote.invalid/v1", "custom_model": "x"},
                ],
                "use_rag": False,
            },
        )
        self.assertEqual(r_bad_custom.status_code, 400)

    def test_searxng_ssrf_guard_html_strip_and_search(self) -> None:
        self.assertFalse(rag_studio_service._is_safe_public_web_url("http://127.0.0.1:8088/config"))
        self.assertFalse(rag_studio_service._is_safe_public_web_url("http://localhost:8765/"))
        self.assertFalse(rag_studio_service._is_safe_public_web_url("http://192.168.1.10/admin"))
        self.assertFalse(rag_studio_service._is_safe_public_web_url("http://10.0.0.5/"))
        self.assertFalse(rag_studio_service._is_safe_public_web_url("http://169.254.169.254/latest/meta-data"))
        self.assertFalse(rag_studio_service._is_safe_public_web_url("http://nas.local/api"))
        self.assertFalse(rag_studio_service._is_safe_public_web_url("file:///etc/passwd"))

        with patch.object(
            rag_studio_service.socket,
            "getaddrinfo",
            return_value=[(2, 1, 6, "", ("93.184.216.34", 443))],
        ):
            self.assertTrue(rag_studio_service._is_safe_public_web_url("https://example.org/docs"))

        with patch.object(
            rag_studio_service.socket,
            "getaddrinfo",
            return_value=[(2, 1, 6, "", ("127.0.0.1", 443))],
        ):
            self.assertFalse(rag_studio_service._is_safe_public_web_url("https://rebind.example.org/"))

        cleaned = rag_studio_service._strip_html_to_text(
            "<html><head><style>body{color:red}</style></head><body>"
            "<script>alert(1)</script><p>Couple &amp; spec <b>RS-04</b></p></body></html>"
        )
        self.assertEqual(cleaned, "Couple & spec RS-04")

        fake_searx = {
            "results": [
                {
                    "title": "RobStride RS-04 Specs",
                    "url": "https://example.org/rs04",
                    "engine": "duckduckgo",
                    "content": "120 Nm pic 48V",
                }
            ]
        }
        with patch.object(rag_studio_service, "_http_get_json", return_value=(fake_searx, None)), \
             patch.object(rag_studio_service, "fetch_public_web_excerpt", return_value="Extrait page publique RS-04"):
            res = rag_studio_service.search_searxng("RobStride RS-04", fetch_pages=True)
            self.assertTrue(res["available"])
            self.assertEqual(len(res["results"]), 1)
            self.assertIn("RESULTATS_RECHERCHE_WEB_SEARXNG", res["context_text"])
            self.assertNotIn("DONNEES NON FIABLES", res["context_text"])
            self.assertIn("Extrait page publique RS-04", res["context_text"])

        sys_web = rag_studio_service.build_system_prompt(use_web=True)
        self.assertIn("RESULTATS_RECHERCHE_WEB_SEARXNG", sys_web)
        self.assertNotIn("DONNEES NON FIABLES", sys_web)

        with patch.object(rag_studio_service, "_http_get_json", return_value=(None, "Connection refused")):
            off = rag_studio_service.search_searxng("test", fetch_pages=False)
            self.assertFalse(off["available"])
            self.assertEqual(off["results"], [])

    def test_searxng_endpoints_and_chat_web_sources(self) -> None:
        with patch.object(
            rag_monitor_ui,
            "start_searxng",
            return_value={"installed": True, "reachable": True, "rss_mb": 31.5},
        ):
            r_start = self.client.post("/api/engines/searxng/start")
            self.assertEqual(r_start.status_code, 200)
            self.assertTrue(r_start.json()["reachable"])

        with patch.object(
            rag_monitor_ui,
            "stop_searxng",
            return_value={"installed": True, "reachable": False, "rss_mb": 0.0},
        ):
            r_stop = self.client.post("/api/engines/searxng/stop")
            self.assertEqual(r_stop.status_code, 200)
            self.assertFalse(r_stop.json()["reachable"])

        fake_web = {
            "available": True,
            "query": "RS-04 CAN",
            "engine_url": "http://127.0.0.1:8088",
            "results": [
                {
                    "index": 1,
                    "title": "Doc RS-04",
                    "url": "https://example.org/rs04",
                    "engine": "duckduckgo",
                    "snippet": "CAN-FD 1 Mbps",
                    "full_excerpt": "CAN-FD 1 Mbps",
                }
            ],
            "context_text": "[RESULTATS_RECHERCHE_WEB_SEARXNG]\nCAN-FD 1 Mbps",
            "error": None,
        }
        with patch.object(rag_monitor_ui, "search_searxng", return_value=fake_web):
            r_search = self.client.post("/api/web/search", json={"query": "RS-04 CAN"})
            self.assertEqual(r_search.status_code, 200)
            self.assertEqual(len(r_search.json()["results"]), 1)

        def _fake_stream(**kwargs):
            yield {"type": "token", "delta": "Reponse avec source web."}
            yield {
                "type": "done",
                "answer": "Reponse avec source web.",
                "thinking": "",
                "mcmaster_refs": [],
                "has_dollar_or_latex": False,
                "metrics": {"profile": "ollama_gemma4", "model": "gemma4:26b", "ttft_s": 0.1, "total_s": 0.3, "tok_per_s": 40.0},
            }

        with patch.object(rag_studio_service, "search_searxng", return_value=fake_web), \
             patch.object(rag_monitor_ui, "stream_llm_chat", side_effect=_fake_stream):
            r_chat = self.client.post(
                "/api/chat/stream",
                json={
                    "query": "Protocole RS-04 ?",
                    "profile": "ollama_gemma4",
                    "context_mode": "none",
                    "use_web": True,
                    "web_categories": "it",
                },
            )
            self.assertEqual(r_chat.status_code, 200)
            self.assertIn("web_sources", r_chat.text)
            self.assertIn("https://example.org/rs04", r_chat.text)


if __name__ == "__main__":
    unittest.main()
