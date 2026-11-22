#!/opt/homebrew/bin/python3.11
"""Tests unitaires isoles pour rag_quality_audit.py et rag_monitor_ui.py.

N'ecrit jamais dans lightrag_dbot_db et ne declenche aucune indexation reelle.
"""

from __future__ import annotations

import base64
import fcntl
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import networkx as nx
import numpy as np
from fastapi.testclient import TestClient

_RAG_DIR = str(Path(__file__).resolve().parent)
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

import rag_chunking  # noqa: E402
import rag_monitor_ui  # noqa: E402
import rag_quality_audit  # noqa: E402
import repair_db_sync  # noqa: E402


def _make_vdb_payload(rows: list[dict], dim: int = 4) -> dict:
    mat = np.zeros((len(rows), dim), dtype=np.float32)
    for idx in range(len(rows)):
        mat[idx, idx % dim] = 1.0
    return {
        "embedding_dim": dim,
        "data": rows,
        "matrix": base64.b64encode(mat.tobytes()).decode("ascii"),
    }


def _seed_synthetic_workspace(root: Path) -> tuple[Path, Path, Path]:
    docs_root = root / "docs"
    db_path = root / "db"
    log_path = root / "rag_indexing.log"
    docs_root.mkdir(parents=True)
    db_path.mkdir(parents=True)

    # 1. Fichier sain (1600/150, bonnes cotes, bon ancrage)
    good_doc = docs_root / "FINAL_Torse.md"
    good_doc.write_text(
        "# Torse\nEpaisseur 12.0 mm, vis 91292A118, couple 45 Nm, alu 7075-T6, poids 2.4 kg, jeu 0.2 mm.",
        encoding="utf-8",
    )

    # 2. Fichier hallucine + legacy 1200/100 (entites hors sujet)
    bad_doc = docs_root / "STUDY_Bad.md"
    bad_doc.write_text(
        "# Bassin\nMoteur RS-06 couple 36 Nm, roulement RB8016 diametre 80 mm, vis 92290A168.",
        encoding="utf-8",
    )

    # 3. Fichier non indexe sur disque
    missing_doc = docs_root / "DOSSIER_TECHNIQUE_Manquant.md"
    missing_doc.write_text("# Nouveau\nContenu non encore indexe.", encoding="utf-8")

    good_id = "doc-good-1"
    bad_id = "doc-bad-2"
    orphan_id = "doc-orphan-9"

    good_chunk = good_id + "-chunk-000"
    bad_chunk = bad_id + "-chunk-000"

    good_cache_ret = (
        "entity<|#|>Torse<|#|>Component<|#|>Epaisseur 12.0 mm, alu 7075-T6, poids 2.4 kg, jeu 0.2 mm\n"
        "entity<|#|>91292A118<|#|>Hardware<|#|>Vis 91292A118 couple 45 Nm\n"
        "relation<|#|>Torse<|#|>91292A118<|#|>fixation<|#|>Fixation a 45 Nm\n"
        "<|COMPLETE|>"
    )
    bad_cache_ret = (
        "entity<|#|>Tortoise Media<|#|>Org<|#|>London journalism outlet\n"
        "entity<|#|>London<|#|>Place<|#|>City in UK"
    )  # Pas de <|COMPLETE|> + entites non ancrees

    (db_path / "indexed_files.json").write_text(
        json.dumps(
            {
                str(good_doc.resolve()): {"mtime": good_doc.stat().st_mtime + 5, "doc_id": good_id},
                str(bad_doc.resolve()): {"mtime": bad_doc.stat().st_mtime + 5, "doc_id": bad_id},
            }
        ),
        encoding="utf-8",
    )
    (db_path / "kv_store_doc_status.json").write_text(
        json.dumps(
            {
                good_id: {
                    "status": "processed",
                    "file_path": "FINAL_Torse.md",
                    "chunks_list": [good_chunk],
                    "metadata": {"chunk_opts": "size=1600, split_only=False, overlap=150"},
                },
                bad_id: {
                    "status": "processed",
                    "file_path": "STUDY_Bad.md",
                    "chunks_list": [bad_chunk],
                    "metadata": {"chunk_opts": "size=1200, split_only=False, overlap=100"},
                },
                orphan_id: {
                    "status": "processed",
                    "file_path": "Archives/Old_Deleted.md",
                    "chunks_list": [],
                    "metadata": {"chunk_opts": "size=1200, split_only=False, overlap=100"},
                },
            }
        ),
        encoding="utf-8",
    )
    (db_path / "kv_store_full_docs.json").write_text(
        json.dumps(
            {
                good_id: {"content": "---\nFichier: FINAL_Torse.md\n---\n" + good_doc.read_text()},
                bad_id: {"content": "---\nFichier: STUDY_Bad.md\n---\n" + bad_doc.read_text()},
                orphan_id: {"content": "---\nFichier: Archives/Old_Deleted.md\n---\nobsolete"},
            }
        ),
        encoding="utf-8",
    )
    (db_path / "kv_store_full_entities.json").write_text(
        json.dumps(
            {
                good_id: {"entity_names": ["Torse", "91292A118"], "count": 2},
                bad_id: {"entity_names": ["Tortoise Media", "London"], "count": 2},
            }
        ),
        encoding="utf-8",
    )
    (db_path / "kv_store_full_relations.json").write_text(
        json.dumps(
            {
                good_id: {"relation_pairs": [["Torse", "91292A118"]], "count": 1},
            }
        ),
        encoding="utf-8",
    )
    (db_path / "kv_store_text_chunks.json").write_text(
        json.dumps(
            {
                good_chunk: {
                    "tokens": 120,
                    "content": good_doc.read_text(),
                    "file_path": "FINAL_Torse.md",
                    "full_doc_id": good_id,
                    "llm_cache_list": ["k_good_1"],
                },
                bad_chunk: {
                    "tokens": 600,
                    "content": bad_doc.read_text(),
                    "file_path": "STUDY_Bad.md",
                    "full_doc_id": bad_id,
                    "llm_cache_list": ["k_bad_1"],
                },
            }
        ),
        encoding="utf-8",
    )
    (db_path / "kv_store_llm_response_cache.json").write_text(
        json.dumps(
            {
                "k_good_1": {"cache_type": "extract", "return": good_cache_ret, "chunk_id": good_chunk},
                "k_bad_1": {"cache_type": "extract", "return": bad_cache_ret, "chunk_id": bad_chunk},
            }
        ),
        encoding="utf-8",
    )
    vdb_chunks = _make_vdb_payload(
        [
            {"__id__": good_chunk, "full_doc_id": good_id, "file_path": "FINAL_Torse.md"},
            {"__id__": bad_chunk, "full_doc_id": bad_id, "file_path": "STUDY_Bad.md"},
        ]
    )
    (db_path / "vdb_chunks.json").write_text(json.dumps(vdb_chunks), encoding="utf-8")
    (db_path / "vdb_entities.json").write_text(json.dumps(_make_vdb_payload([])), encoding="utf-8")
    (db_path / "vdb_relationships.json").write_text(json.dumps(_make_vdb_payload([])), encoding="utf-8")

    g = nx.Graph()
    g.add_node("Torse", entity_type="Component", source_id=good_chunk, description="Torse D-Bot")
    g.add_node("91292A118", entity_type="Hardware", source_id=good_chunk, description="Vis M4")
    g.add_edge("Torse", "91292A118", keywords="fixation", source_id=good_chunk)
    g.add_node("NoeudIsole", entity_type="Misc", source_id=bad_chunk, description="Orphelin degre 0")
    nx.write_graphml(g, db_path / "graph_chunk_entity_relation.graphml")

    log_path.write_text(
        "[22:19:42] INFO: 🦙 Moteur d'indexation actif : Ollama (qwen3.8:27b-mlx)\n"
        "[22:20:01] INFO: [  1/  5] 📄 FINAL_Torse.md [🦙 Ollama]\n",
        encoding="utf-8",
    )
    return docs_root, db_path, log_path


class TestRagQualityMonitor(unittest.TestCase):
    def test_audit_scoring_detects_missing_hallucinated_and_healthy_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docs_root, db_path, log_path = _seed_synthetic_workspace(Path(tmp))
            with patch.object(rag_quality_audit, "_detect_running_index_pids", return_value=[]):
                report = rag_quality_audit.run_full_audit(
                    db_path=db_path, docs_root=docs_root, log_path=log_path
                )

            by_rel = {d["rel_path"]: d for d in report["documents"]}
            self.assertEqual(by_rel["DOSSIER_TECHNIQUE_Manquant.md"]["score"], 0)
            self.assertIn("NOT_INDEXED", by_rel["DOSSIER_TECHNIQUE_Manquant.md"]["reasons"])

            bad = by_rel["STUDY_Bad.md"]
            self.assertEqual(bad["health_status"], "critical")
            self.assertIn("LEGACY_1200_100", bad["reasons"])
            self.assertIn("UNGROUNDED_ENTITIES", bad["reasons"])
            self.assertIn("MISSING_COMPLETE_TAG", bad["reasons"])

            good = by_rel["FINAL_Torse.md"]
            self.assertEqual(good["health_status"], "healthy")
            self.assertGreaterEqual(good["score"], 85)

            self.assertEqual(report["summary"]["orphans_count"], 1)
            self.assertEqual(report["graph_health"]["degree_zero_nodes"], 1)

            html_out = rag_quality_audit.export_static_html_report(report)
            self.assertIn("STUDY_Bad.md", html_out)
            self.assertIn("FINAL_Torse.md", html_out)

    def test_safe_read_json_tolerates_corrupted_transient_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / "partial.json"
            broken.write_text('{"incomplete": ', encoding="utf-8")
            data, err = rag_quality_audit._safe_read_json(broken, retries=2, delay_s=0.01)
            self.assertIsNone(data)
            self.assertIsNotNone(err)

    def test_fastapi_endpoints_and_lock_protection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs_root, db_path, log_path = _seed_synthetic_workspace(root)
            bench_path = root / "bench.json"
            bench_path.write_text(
                json.dumps(
                    {
                        "benchmark_name": "Test Bench",
                        "data_recipes_qa": [
                            {
                                "id": "q1",
                                "category": "bom",
                                "source_doc": "FINAL_Torse.md",
                                "question": "Quelle vis fixe le torse ?",
                                "numeric_token": "91292A118",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            app = rag_monitor_ui.create_app(
                db_path=db_path,
                docs_root=docs_root,
                log_path=log_path,
                benchmark_path=bench_path,
                audit_md_path=root / "AUDIT_INTEGRITE.md",
            )
            client = TestClient(app)

            with patch.object(rag_quality_audit, "_detect_running_index_pids", return_value=[]):
                self.assertEqual(client.get("/").status_code, 200)
                audit_resp = client.get("/api/audit")
                self.assertEqual(audit_resp.status_code, 200)
                self.assertEqual(audit_resp.json()["summary"]["disk_files_count"], 3)

                det = client.get("/api/file", params={"rel_path": "FINAL_Torse.md"})
                self.assertEqual(det.status_code, 200)
                self.assertEqual(len(det.json()["chunks"]), 1)
                self.assertGreaterEqual(len(det.json()["subgraph"]["nodes"]), 2)

                # Blocage path traversal
                bad_path = client.get("/api/file", params={"rel_path": "../secret.txt"})
                self.assertEqual(bad_path.status_code, 400)

                # Export HTML
                exp = client.get("/api/export/html")
                self.assertEqual(exp.status_code, 200)
                self.assertIn("text/html", exp.headers["content-type"])

            # Simulation d'un verrou .indexing.lock actif -> HTTP 409 sur re-indexation
            lock_file = db_path / ".indexing.lock"
            with lock_file.open("a+", encoding="utf-8") as fh:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                try:
                    st = client.get("/api/status").json()
                    self.assertTrue(st["indexing_active"])
                    reidx = client.post(
                        "/api/actions/reindex",
                        json={"rel_paths": ["STUDY_Bad.md"], "provider": "ollama"},
                    )
                    self.assertEqual(reidx.status_code, 409)
                finally:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)

    def test_readonly_vector_searcher_and_benchmark_with_stub_embedder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs_root, db_path, _ = _seed_synthetic_workspace(root)
            bench_path = root / "bench.json"
            bench_path.write_text(
                json.dumps(
                    {
                        "benchmark_name": "Test Bench",
                        "data_recipes_qa": [
                            {
                                "id": "q1",
                                "category": "bom",
                                "source_doc": "FINAL_Torse.md",
                                "question": "vis 91292A118",
                                "numeric_token": "91292A118",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            class _FakeEmbed:
                def embed(self, texts):
                    for _ in texts:
                        yield np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)

            searcher = rag_monitor_ui._ReadOnlyVectorSearcher(db_path=db_path)
            searcher._embed_model = _FakeEmbed()
            hits = searcher.search("vis 91292A118", top_k=2, use_reranker=False)
            self.assertEqual(hits[0]["file_path"], "FINAL_Torse.md")

            bench_res = rag_monitor_ui._run_benchmark_eval(
                searcher, bench_path, top_k=5, use_reranker=False
            )
            self.assertEqual(bench_res["recall_at_1"], 1.0)
            self.assertEqual(bench_res["numeric_token_hit_rate"], 1.0)

            # Test resolution canonique d'un chunk de section sans en-tete Fichier et rappel lexical rare
            fd = json.loads((db_path / "kv_store_full_docs.json").read_text(encoding="utf-8"))
            tc = json.loads((db_path / "kv_store_text_chunks.json").read_text(encoding="utf-8"))
            vdb_c = json.loads((db_path / "vdb_chunks.json").read_text(encoding="utf-8"))
            fd["doc-sec-bom"] = {"content": "---\nFichier: 05_Gestion_Projet/FINAL_BOM.md\nSection: 1-visserie\n---\nTexte"}
            tc["doc-sec-bom-chunk-000"] = {
                "tokens": 20,
                "content": "Support Batterie Central vis 92290A161 couple 2,2 Nm inox 316.",
                "file_path": "FINAL_BOM--sec-1-visserie--abc123.md",
                "full_doc_id": "doc-sec-bom",
            }
            rows = list(vdb_c["data"]) + [
                {
                    "__id__": "doc-sec-bom-chunk-000",
                    "full_doc_id": "doc-sec-bom",
                    "file_path": "FINAL_BOM--sec-1-visserie--abc123.md",
                }
            ]
            mat = np.zeros((len(rows), 4), dtype=np.float32)
            for idx in range(len(rows) - 1):
                mat[idx, idx % 4] = 1.0
            mat[-1, 1] = 1.0  # orthogonal au vecteur [1, 0, 0, 0] -> sauve uniquement par rappel lexical
            vdb_payload = {
                "embedding_dim": 4,
                "data": rows,
                "matrix": base64.b64encode(mat.tobytes()).decode("ascii"),
            }
            (db_path / "kv_store_full_docs.json").write_text(json.dumps(fd), encoding="utf-8")
            (db_path / "kv_store_text_chunks.json").write_text(json.dumps(tc), encoding="utf-8")
            (db_path / "vdb_chunks.json").write_text(json.dumps(vdb_payload), encoding="utf-8")

            lex_hits = searcher.search("couple serrage Support Batterie Central 92290A161 2,2 Nm", top_k=3, use_reranker=False)
            bom_hit = next((h for h in lex_hits if h["chunk_id"] == "doc-sec-bom-chunk-000"), None)
            self.assertIsNotNone(bom_hit)
            self.assertEqual(bom_hit["file_path"], "05_Gestion_Projet/FINAL_BOM.md")
            self.assertEqual(bom_hit["section_key"], "1-visserie")

    def test_detect_live_status_parses_chunk_progress_and_processing_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, db_path, log_path = _seed_synthetic_workspace(root)
            ds = json.loads((db_path / "kv_store_doc_status.json").read_text(encoding="utf-8"))
            ds["doc-proc-1"] = {
                "status": "processing",
                "file_path": "DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md",
                "chunks_count": 40,
                "metadata": {"process_start_time": 1700000000},
            }
            (db_path / "kv_store_doc_status.json").write_text(json.dumps(ds), encoding="utf-8")
            log_path.write_text(
                "[22:19:42] INFO: 🦙 Moteur d'indexation actif : Ollama (qwen3.8:27b-mlx)\n"
                "[22:20:01] INFO: [  1/  5] 📄 DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md [🦙 Ollama]\n"
                "[22:21:10] INFO: 🦙 [Ollama #5] gleaning en cours (qwen3.8:27b-mlx, ~14000 car.)...\n"
                "[22:21:25] INFO: Chunk 3 of 40 extracted 19 Ent + 14 Rel doc-proc-1-chunk-002\n",
                encoding="utf-8",
            )
            with patch.object(rag_quality_audit, "_detect_running_index_pids", return_value=[99999]), patch.object(
                rag_quality_audit,
                "_probe_ollama_ps",
                return_value=[{"name": "qwen3.8:27b-mlx", "size_vram_gb": 24.58, "context_length": 16384, "runner": "mlx"}],
            ):
                live = rag_quality_audit.detect_live_indexing_status(db_path=db_path, log_path=log_path)

            self.assertTrue(live["indexing_active"])
            self.assertEqual(live["current_chunk_progress"], "Chunk 3/40 (19 Ent + 14 Rel)")
            self.assertIn("Ollama #5", live["last_ollama_call"])
            self.assertEqual(len(live["processing_docs"]), 1)
            self.assertEqual(live["processing_docs"][0]["chunks_count"], 40)
            self.assertEqual(live["ollama_ps"][0]["name"], "qwen3.8:27b-mlx")

    def test_detect_live_status_filters_unit_test_bursts_from_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, db_path, log_path = _seed_synthetic_workspace(root)
            log_path.write_text(
                "[22:16:11] INFO: [  1/49] 📄 DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md [💎 Gemini]\n"
                "[22:20:44] INFO: 🦙 Moteur d'indexation actif : Ollama (qwen3.8:27b-mlx)\n"
                "[22:53:53] INFO: 🦙 Moteur d'indexation actif : Ollama (gemma4:26b)\n"
                "[22:53:53] INFO: [  1/1] 📄 sample.md\n"
                "[22:53:53] WARNING: TestRagResilience mock line\n",
                encoding="utf-8",
            )
            with patch.object(rag_quality_audit, "_detect_running_index_pids", return_value=[99999]), patch.object(
                rag_quality_audit, "_probe_ollama_ps", return_value=[]
            ):
                live = rag_quality_audit.detect_live_indexing_status(db_path=db_path, log_path=log_path)

            self.assertEqual(live["active_engine"], "Ollama (qwen3.8:27b-mlx)")
            self.assertIn("DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md", live["current_progress"])
            self.assertEqual(live["last_log_time"], "22:20:44")

    def test_audit_aggregates_virtual_sections_and_respects_normalized_sha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs_root, db_path, log_path = _seed_synthetic_workspace(root)
            sec_doc = docs_root / "DOSSIER_Sectioned.md"
            sec_text = (
                "# Dossier Sec\n\n"
                "## 📑 Sommaire\n- [1. Intro](#1-intro)\n\n"
                "## 1. Intro\nMoteur RS-04 couple 40 Nm.\n\n"
                "## 2. Cadre\nChassis aluminium 7075-T6 epaisseur 10 mm.\n"
            )
            sec_doc.write_text(sec_text, encoding="utf-8")
            norm_sha = rag_chunking.compute_normalized_sha256(sec_text, ext=".md")

            ds = json.loads((db_path / "kv_store_doc_status.json").read_text(encoding="utf-8"))
            fd = json.loads((db_path / "kv_store_full_docs.json").read_text(encoding="utf-8"))
            fe = json.loads((db_path / "kv_store_full_entities.json").read_text(encoding="utf-8"))
            fr = json.loads((db_path / "kv_store_full_relations.json").read_text(encoding="utf-8"))
            tc = json.loads((db_path / "kv_store_text_chunks.json").read_text(encoding="utf-8"))
            cache = json.loads((db_path / "kv_store_llm_response_cache.json").read_text(encoding="utf-8"))
            idx = json.loads((db_path / "indexed_files.json").read_text(encoding="utf-8"))

            s1_id, s2_id = "doc-sec-1", "doc-sec-2"
            c1, c2 = "doc-sec-1-chunk-000", "doc-sec-2-chunk-000"
            for did, sk, fp, cid, txt, ent in (
                (s1_id, "1-intro", "DOSSIER_Sectioned--sec-1.md", c1, "Moteur RS-04 couple 40 Nm.", "RS-04"),
                (s2_id, "2-cadre", "DOSSIER_Sectioned--sec-2.md", c2, "Chassis aluminium 7075-T6 epaisseur 10 mm.", "7075-T6"),
            ):
                ds[did] = {
                    "status": "processed",
                    "file_path": fp,
                    "chunks_list": [cid],
                    "metadata": {"chunk_opts": "size=1600, overlap=150"},
                }
                fd[did] = {"content": f"---\nFichier: DOSSIER_Sectioned.md\nSection: {sk}\n---\n{txt}"}
                fe[did] = {"entity_names": [ent], "count": 1}
                fr[did] = {"relation_pairs": [[ent, "D-Bot"]], "count": 1}
                tc[cid] = {"tokens": 60, "content": txt, "file_path": fp, "full_doc_id": did, "llm_cache_list": [f"k_{did}"]}
                cache[f"k_{did}"] = {
                    "cache_type": "extract",
                    "chunk_id": cid,
                    "return": f"entity<|#|>D-Bot<|#|>System<|#|>Robot\nentity<|#|>{ent}<|#|>Part<|#|>Spec {txt}\nrelation<|#|>{ent}<|#|>D-Bot<|#|>use<|#|>OK\n<|COMPLETE|>",
                }

            # Simule mtime plus recent sur disque mais meme content_sha256 (edition pure de sommaire)
            idx[str(sec_doc.resolve())] = {
                "mtime": sec_doc.stat().st_mtime - 50,
                "doc_id": s1_id,
                "content_sha256": norm_sha,
                "sections": {
                    "1-intro": {"doc_id": s1_id, "sha256": "a"},
                    "2-cadre": {"doc_id": s2_id, "sha256": "b"},
                },
            }
            vdb_c = _make_vdb_payload(
                [
                    {"__id__": "doc-good-1-chunk-000", "full_doc_id": "doc-good-1", "file_path": "FINAL_Torse.md"},
                    {"__id__": "doc-bad-2-chunk-000", "full_doc_id": "doc-bad-2", "file_path": "STUDY_Bad.md"},
                    {"__id__": c1, "full_doc_id": s1_id, "file_path": "DOSSIER_Sectioned--sec-1.md"},
                    {"__id__": c2, "full_doc_id": s2_id, "file_path": "DOSSIER_Sectioned--sec-2.md"},
                ]
            )
            (db_path / "kv_store_doc_status.json").write_text(json.dumps(ds), encoding="utf-8")
            (db_path / "kv_store_full_docs.json").write_text(json.dumps(fd), encoding="utf-8")
            (db_path / "kv_store_full_entities.json").write_text(json.dumps(fe), encoding="utf-8")
            (db_path / "kv_store_full_relations.json").write_text(json.dumps(fr), encoding="utf-8")
            (db_path / "kv_store_text_chunks.json").write_text(json.dumps(tc), encoding="utf-8")
            (db_path / "kv_store_llm_response_cache.json").write_text(json.dumps(cache), encoding="utf-8")
            (db_path / "indexed_files.json").write_text(json.dumps(idx), encoding="utf-8")
            (db_path / "vdb_chunks.json").write_text(json.dumps(vdb_c), encoding="utf-8")

            with patch.object(rag_quality_audit, "_detect_running_index_pids", return_value=[]):
                report = rag_quality_audit.run_full_audit(
                    db_path=db_path, docs_root=docs_root, log_path=log_path
                )
            by_rel = {d["rel_path"]: d for d in report["documents"]}
            sec_entry = by_rel["DOSSIER_Sectioned.md"]
            self.assertEqual(sec_entry["chunks_count"], 2)
            self.assertEqual(sec_entry["entities_count"], 2)
            self.assertNotIn("DUPLICATE_DOC_IDS", sec_entry["reasons"])
            self.assertNotIn("STALE_MTIME", sec_entry["reasons"])

            detail = rag_quality_audit.inspect_document_detail(
                "DOSSIER_Sectioned.md", db_path=db_path, docs_root=docs_root
            )
            self.assertEqual(len(detail["chunks"]), 2)

    def test_repair_db_sync_full_hygiene_and_compaction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs_root, db_path, _ = _seed_synthetic_workspace(root)
            # Ajoute fichiers exclus sur disque (Code/rag/*.py + test_*.py) + doublon unknown_source + cache orphelin
            excl_py = docs_root / "Code" / "rag" / "index_docs.py"
            excl_py.parent.mkdir(parents=True, exist_ok=True)
            excl_py.write_text("# rag plumbing", encoding="utf-8")

            ds = json.loads((db_path / "kv_store_doc_status.json").read_text(encoding="utf-8"))
            fd = json.loads((db_path / "kv_store_full_docs.json").read_text(encoding="utf-8"))
            tc = json.loads((db_path / "kv_store_text_chunks.json").read_text(encoding="utf-8"))
            cache = json.loads((db_path / "kv_store_llm_response_cache.json").read_text(encoding="utf-8"))
            vdb_c = json.loads((db_path / "vdb_chunks.json").read_text(encoding="utf-8"))

            # Doublon ancien pour FINAL_Torse.md en 'unknown_source' + doc exclu Code/rag/index_docs.py
            ds["doc-good-old"] = {
                "status": "processed",
                "file_path": "unknown_source",
                "chunks_list": ["chunk-old"],
                "metadata": {"chunk_opts": "size=1200, overlap=100"},
            }
            fd["doc-good-old"] = {"content": "---\nFichier: FINAL_Torse.md\n---\nold content"}
            ds["doc-excl-py"] = {
                "status": "processed",
                "file_path": "index_docs.py",
                "chunks_list": ["chunk-excl"],
                "metadata": {"chunk_opts": "size=1600, overlap=150"},
            }
            fd["doc-excl-py"] = {"content": "---\nFichier: Code/rag/index_docs.py\n---\n# rag"}
            tc["chunk-old"] = {"tokens": 10, "content": "old", "file_path": "unknown_source", "full_doc_id": "doc-good-old", "llm_cache_list": ["k_orphan"]}
            tc["chunk-excl"] = {"tokens": 10, "content": "# rag", "file_path": "index_docs.py", "full_doc_id": "doc-excl-py", "llm_cache_list": ["k_excl"]}
            cache["k_orphan"] = {"cache_type": "extract", "chunk_id": "chunk-old", "return": "orphan"}
            cache["k_excl"] = {"cache_type": "extract", "chunk_id": "chunk-excl", "return": "excl"}
            cache["k_unreferenced"] = {"cache_type": "extract", "chunk_id": "chunk-gone", "return": "gone"}

            vdb_c = _make_vdb_payload(
                list(vdb_c["data"])
                + [
                    {"__id__": "chunk-old", "full_doc_id": "doc-good-old", "file_path": "unknown_source"},
                    {"__id__": "chunk-excl", "full_doc_id": "doc-excl-py", "file_path": "index_docs.py"},
                ]
            )
            (db_path / "kv_store_doc_status.json").write_text(json.dumps(ds), encoding="utf-8")
            (db_path / "kv_store_full_docs.json").write_text(json.dumps(fd), encoding="utf-8")
            (db_path / "kv_store_text_chunks.json").write_text(json.dumps(tc), encoding="utf-8")
            (db_path / "kv_store_llm_response_cache.json").write_text(json.dumps(cache), encoding="utf-8")
            (db_path / "vdb_chunks.json").write_text(json.dumps(vdb_c), encoding="utf-8")

            rc = repair_db_sync.run_repair(
                db_path,
                apply=True,
                make_backup=False,
                docs_root=docs_root,
                dedupe_docs=True,
                purge_excluded=True,
                compact_cache=True,
            )
            self.assertEqual(rc, 0)

            ds_after = json.loads((db_path / "kv_store_doc_status.json").read_text(encoding="utf-8"))
            self.assertEqual(set(ds_after.keys()), {"doc-good-1", "doc-bad-2"})
            cache_after = json.loads((db_path / "kv_store_llm_response_cache.json").read_text(encoding="utf-8"))
            self.assertEqual(set(cache_after.keys()), {"k_good_1", "k_bad_1"})
            vdb_after = json.loads((db_path / "vdb_chunks.json").read_text(encoding="utf-8"))
            self.assertEqual(len(vdb_after["data"]), 2)

    def test_v2_monitor_api_storage_sections_reindex_and_hygiene(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs_root, db_path, log_path = _seed_synthetic_workspace(root)
            (docs_root / "notes_reglage.md").write_text("# Notes\nReglage bus CAN 5 Mbps.", encoding="utf-8")
            sec_doc = docs_root / "DOSSIER_Sectioned.md"
            sec_doc.write_text("# Doc Sec\n\n## 1. Intro\nDetail intro.\n\n## 2. Cadre\nDetail cadre.\n", encoding="utf-8")

            ds = json.loads((db_path / "kv_store_doc_status.json").read_text(encoding="utf-8"))
            fd = json.loads((db_path / "kv_store_full_docs.json").read_text(encoding="utf-8"))
            fe = json.loads((db_path / "kv_store_full_entities.json").read_text(encoding="utf-8"))
            fr = json.loads((db_path / "kv_store_full_relations.json").read_text(encoding="utf-8"))
            tc = json.loads((db_path / "kv_store_text_chunks.json").read_text(encoding="utf-8"))
            cache = json.loads((db_path / "kv_store_llm_response_cache.json").read_text(encoding="utf-8"))
            idx = json.loads((db_path / "indexed_files.json").read_text(encoding="utf-8"))
            vdb_c = json.loads((db_path / "vdb_chunks.json").read_text(encoding="utf-8"))

            for did, sk, cid, txt in (
                ("doc-s1", "1-intro", "doc-s1-chunk-000", "Detail intro."),
                ("doc-s2", "2-cadre", "doc-s2-chunk-000", "Detail cadre."),
            ):
                ds[did] = {"status": "processed", "file_path": f"DOSSIER_Sectioned--sec-{sk}.md", "chunks_list": [cid], "metadata": {"chunk_opts": "size=1600, overlap=150"}}
                fd[did] = {"content": f"---\nFichier: DOSSIER_Sectioned.md\nSection: {sk}\n---\n{txt}"}
                fe[did] = {"entity_names": ["D-Bot"], "count": 1}
                fr[did] = {"relation_pairs": [], "count": 0}
                tc[cid] = {"tokens": 30, "content": txt, "file_path": f"DOSSIER_Sectioned--sec-{sk}.md", "full_doc_id": did, "llm_cache_list": []}
            idx[str(sec_doc.resolve())] = {
                "mtime": sec_doc.stat().st_mtime + 10,
                "doc_id": "doc-s1",
                "content_sha256": rag_chunking.compute_normalized_sha256(sec_doc.read_text(encoding="utf-8"), ext=".md"),
                "sections": {"1-intro": {"doc_id": "doc-s1", "sha256": "a"}, "2-cadre": {"doc_id": "doc-s2", "sha256": "b"}},
            }
            vdb_c = _make_vdb_payload(
                list(vdb_c["data"])
                + [
                    {"__id__": "doc-s1-chunk-000", "full_doc_id": "doc-s1", "file_path": "DOSSIER_Sectioned--sec-1-intro.md"},
                    {"__id__": "doc-s2-chunk-000", "full_doc_id": "doc-s2", "file_path": "DOSSIER_Sectioned--sec-2-cadre.md"},
                ]
            )
            (db_path / "kv_store_doc_status.json").write_text(json.dumps(ds), encoding="utf-8")
            (db_path / "kv_store_full_docs.json").write_text(json.dumps(fd), encoding="utf-8")
            (db_path / "kv_store_full_entities.json").write_text(json.dumps(fe), encoding="utf-8")
            (db_path / "kv_store_full_relations.json").write_text(json.dumps(fr), encoding="utf-8")
            (db_path / "kv_store_text_chunks.json").write_text(json.dumps(tc), encoding="utf-8")
            (db_path / "kv_store_llm_response_cache.json").write_text(json.dumps(cache), encoding="utf-8")
            (db_path / "indexed_files.json").write_text(json.dumps(idx), encoding="utf-8")
            (db_path / "vdb_chunks.json").write_text(json.dumps(vdb_c), encoding="utf-8")

            log_path.write_text(
                "[23:10:01] INFO: 🦙 Moteur d'indexation actif : Ollama (qwen3.8:27b-mlx)\n"
                "[23:10:02] INFO: 📦 Insertion lot LightRAG (2 doc(s), gleaning=1 : FINAL_Torse.md, STUDY_Bad.md)...\n"
                "[23:10:09] INFO:   - Résumés de fusion (deterministic): deterministe=3, gemma4=0, force_llm_summary_on_merge=24\n",
                encoding="utf-8",
            )
            live = rag_quality_audit.detect_live_indexing_status(db_path=db_path, log_path=log_path)
            self.assertIn("2 doc(s), gleaning=1", live["current_batch"])
            self.assertIn("deterministic:", live["summary_stats_line"])

            app = rag_monitor_ui.create_app(db_path=db_path, docs_root=docs_root, log_path=log_path)
            client = TestClient(app)
            with patch.object(rag_quality_audit, "_detect_running_index_pids", return_value=[]):
                html_txt = client.get("/").text
                self.assertIn('id="re-gleaning"', html_txt)
                self.assertIn('id="btn-run-hygiene"', html_txt)
                self.assertIn('id="storage-pill"', html_txt)

                audit_json = client.get("/api/audit").json()
                self.assertIn("storage", audit_json)
                self.assertEqual(audit_json["summary"]["sectioned_files_count"], 1)
                self.assertEqual(audit_json["summary"]["virtual_sections_total"], 2)
                by_rel = {d["rel_path"]: d for d in audit_json["documents"]}
                self.assertEqual(by_rel["FINAL_Torse.md"]["gleaning_policy"], 1)
                self.assertEqual(by_rel["notes_reglage.md"]["gleaning_policy"], 0)
                self.assertEqual(by_rel["DOSSIER_Sectioned.md"]["sections_count"], 2)

                det = client.get("/api/file", params={"rel_path": "DOSSIER_Sectioned.md"}).json()
                self.assertEqual([c["section_key"] for c in det["chunks"]], ["1-intro", "2-cadre"])

                bad_reidx = client.post(
                    "/api/actions/reindex",
                    json={"rel_paths": ["FINAL_Torse.md"], "gleaning_mode": "bogus"},
                )
                self.assertEqual(bad_reidx.status_code, 400)

                class _FakeProc:
                    def __init__(self, pid: int = 42424) -> None:
                        self.pid = pid

                with patch.object(rag_monitor_ui.subprocess, "Popen", return_value=_FakeProc()) as popen_mock:
                    ok_reidx = client.post(
                        "/api/actions/reindex",
                        json={
                            "rel_paths": ["FINAL_Torse.md"],
                            "provider": "auto",
                            "summary_mode": "deterministic",
                            "gleaning_mode": "adaptive",
                            "batch_size": 8,
                            "mirror_backup": True,
                        },
                    )
                    self.assertEqual(ok_reidx.status_code, 202)
                    cmd_reidx = popen_mock.call_args[0][0]
                    for arg in ("--provider", "auto", "--summary-mode", "deterministic", "--gleaning-mode", "adaptive", "--batch-size", "8", "--mirror-backup", "--files", "FINAL_Torse.md"):
                        self.assertIn(arg, cmd_reidx)

                    ok_hyg = client.post(
                        "/api/actions/hygiene",
                        json={"full_hygiene": True, "sync_mirror": True, "dry_run": False},
                    )
                    self.assertEqual(ok_hyg.status_code, 202)
                    cmd_hyg = popen_mock.call_args[0][0]
                    self.assertTrue(cmd_hyg[1].endswith("repair_db_sync.py"))
                    for arg in ("--full-hygiene", "--apply", "--no-backup", "--sync-mirror"):
                        self.assertIn(arg, cmd_hyg)

                # Verrou actif -> HTTP 409 sur /api/actions/hygiene aussi
                lock_file = db_path / ".indexing.lock"
                with lock_file.open("a+", encoding="utf-8") as fh:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    try:
                        locked_hyg = client.post("/api/actions/hygiene", json={})
                        self.assertEqual(locked_hyg.status_code, 409)
                    finally:
                        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)

    def test_live_status_reads_progress_json_and_ignores_stale_log(self) -> None:
        import os  # noqa: E402
        import time  # noqa: E402

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, db_path, log_path = _seed_synthetic_workspace(root)
            log_path.write_text(
                "[22:19:42] INFO: [  1/ 49] 📄 OLD_FILE.md [🦙 Ollama]\n",
                encoding="utf-8",
            )
            old_ts = time.time() - 3600
            os.utime(log_path, (old_ts, old_ts))

            (db_path / ".indexing_progress.json").write_text(
                json.dumps(
                    {
                        "phase": "insert",
                        "started_at": time.time() - 45,
                        "total_files": 16,
                        "done_files": 10,
                        "total_units": 20,
                        "done_units": 12,
                        "failed_units": 0,
                        "current_batch_index": 2,
                        "total_batches": 3,
                        "current_batch_gleaning": 0,
                        "current_batch_files": ["A.md", "B.md"],
                        "active_engine": "gemini-3.6-flash",
                    }
                ),
                encoding="utf-8",
            )
            lock_file = db_path / ".indexing.lock"
            with lock_file.open("a+", encoding="utf-8") as fh:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                try:
                    with patch.object(rag_quality_audit, "_detect_running_index_pids", return_value=[]):
                        live = rag_quality_audit.detect_live_indexing_status(db_path=db_path, log_path=log_path)
                    self.assertTrue(live["indexing_active"])
                    self.assertIsNotNone(live["progress"])
                    self.assertEqual(live["progress"]["pct"], 60.0)
                    self.assertEqual(live["progress"]["done_units"], 12)
                    self.assertEqual(live["active_engine"], "gemini-3.6-flash")
                    self.assertIn("12/20", live["current_progress"])
                    self.assertNotIn("OLD_FILE.md", live["current_progress"])
                finally:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


if __name__ == "__main__":
    unittest.main()
