"""
Vector DB Importer & FAISS Indexing Pipeline (backend/app/services/vector_importer.py)
Ports VectorImport architecture into the core backend.
Manages project-isolated FAISS L2 vector stores and background indexing.
"""

import os
import json
import hashlib
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

EMBEDDING_DIM = 384
VECTOR_STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vector_store")

class VectorImporter:
    def __init__(self, storage_dir: str = VECTOR_STORE_DIR):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def compute_embedding(self, text: str) -> np.ndarray:
        """
        Generates a normalized 384-dimensional dense float32 vector for text.
        Multi-hash projection technique matching VectorImport EmbeddingService.
        """
        vec = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        words = text.lower().split()
        for idx, word in enumerate(words):
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            bucket = h % EMBEDDING_DIM
            val = ((h >> 8) % 200 - 100) / 100.0
            vec[bucket] += val

            if idx > 0:
                bigram = f"{words[idx-1]}_{word}"
                h_bi = int(hashlib.md5(bigram.encode("utf-8")).hexdigest(), 16)
                bucket_bi = h_bi % EMBEDDING_DIM
                vec[bucket_bi] += ((h_bi >> 8) % 200 - 100) / 100.0

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def assemble_project_chunks(self, project_code: str) -> List[Dict[str, Any]]:
        """
        Assembles all documents, tasks, chat logs, and RAID items for a project into chunks.
        """
        chunks = []

        # 1. Read tasks & RAID from app.db
        app_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "app.db")
        if os.path.exists(app_db_path):
            try:
                conn = sqlite3.connect(app_db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("SELECT id, name, code, lifecycle_phase FROM projects WHERE code = ?", (project_code,))
                proj = cursor.fetchone()
                if proj:
                    p_id = proj['id']
                    cursor.execute("SELECT id, wbs_code, title, status, priority FROM tasks WHERE project_id = ?", (p_id,))
                    for t in cursor.fetchall():
                        text_content = f"WBS Task [{t['wbs_code']}] {t['title']} (Status: {t['status']}, Priority: {t['priority']})"

                        chunks.append({
                            "chunk_id": f"chk_{project_code}_task_{t['id']}",
                            "doc_id": f"doc_{project_code}_tasks",
                            "source": "TaskAdapter",
                            "title": t['title'],
                            "text": text_content,
                            "metadata": {
                                "project_code": project_code,
                                "type": "task",
                                "wbs_code": t['wbs_code'],
                                "status": t['status']
                            }
                        })

                    cursor.execute("SELECT id, category, title, description, risk_score, owner_name FROM raid_items WHERE project_id = ?", (p_id,))
                    for r in cursor.fetchall():
                        text_content = f"RAID Item [{r['category']}] {r['title']}: {r['description']} (Score: {r['risk_score']}, Owner: {r['owner_name']})"
                        chunks.append({
                            "chunk_id": f"chk_{project_code}_raid_{r['id']}",
                            "doc_id": f"doc_{project_code}_raid",
                            "source": "RiskRegisterAdapter",
                            "title": r['title'],
                            "text": text_content,
                            "metadata": {
                                "project_code": project_code,
                                "type": "raid",
                                "category": r['category'],
                                "risk_score": r['risk_score']
                            }
                        })
                conn.close()
            except Exception as e:
                print(f"[VectorImporter app.db Read Error] {e}")

        # 2. Read communication logs from mcp.db
        mcp_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "mcp", "mcp.db")
        if os.path.exists(mcp_db_path):
            try:
                conn = sqlite3.connect(mcp_db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT id, source_type, sender, receiver, message_text FROM communication_logs WHERE project_code = ?", (project_code,))
                for c in cursor.fetchall():
                    text_content = f"Communication Log [{c['source_type']}] {c['sender']} -> {c['receiver']}: {c['message_text']}"
                    chunks.append({
                        "chunk_id": f"chk_{project_code}_comm_{c['id']}",
                        "doc_id": f"doc_{project_code}_comms",
                        "source": "ChatAdapter",
                        "title": f"Chat from {c['sender']}",
                        "text": text_content,
                        "metadata": {
                            "project_code": project_code,
                        }
                    })
                conn.close()
            except Exception as e:
                print(f"[VectorImporter mcp.db Read Error] {e}")


        # 3. Read uploaded policy & project text files from backend/app/uploads/
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        if os.path.exists(uploads_dir):
            try:

                for fname in os.listdir(uploads_dir):
                    if fname.endswith('.txt') and not fname.startswith('.'):
                        filepath = os.path.join(uploads_dir, fname)
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
                            file_text = fh.read().strip()
                            if file_text:
                                file_paragraphs = [p.strip() for p in file_text.split('\n\n') if p.strip()]
                                for p_idx, para in enumerate(file_paragraphs):
                                    chunks.append({
                                        "chunk_id": f"chk_{project_code}_doc_{fname}_{p_idx}",
                                        "doc_id": f"doc_file_{fname}",
                                        "source": "FileAdapter",
                                        "title": f"Document: {fname}",
                                        "text": f"Document [{fname}]: {para}",
                                        "metadata": {
                                            "project_code": project_code,
                                            "type": "file",
                                            "filename": fname
                                        }
                                    })
            except Exception as e:
                print(f"[VectorImporter Uploads File Read Error] {e}")

        return chunks


    def index_project(self, project_code: str) -> str:
        """
        Indexes all text chunks for a project into a dedicated FAISS vector file or numpy matrix.
        """
        chunks = self.assemble_project_chunks(project_code)
        safe_proj_code = project_code.replace("-", "_").lower()
        faiss_file = self.storage_dir / f"project_{safe_proj_code}_index.faiss"
        npy_file = self.storage_dir / f"project_{safe_proj_code}_vectors.npy"
        meta_file = self.storage_dir / f"project_{safe_proj_code}_metadata.json"

        if chunks:
            vectors = np.array([self.compute_embedding(c["text"]) for c in chunks], dtype=np.float32)
        else:
            vectors = np.zeros((0, EMBEDDING_DIM), dtype=np.float32)

        if HAS_FAISS:
            index = faiss.IndexFlatL2(EMBEDDING_DIM)
            if len(vectors) > 0:
                index.add(vectors)
            faiss.write_index(index, str(faiss_file))
        else:
            np.save(str(npy_file), vectors)

        chunk_metadata = [
            {
                "index_pos": idx,
                "chunk_id": c["chunk_id"],
                "doc_id": c["doc_id"],
                "source": c["source"],
                "title": c["title"],
                "text": c["text"],
                "metadata": c.get("metadata", {})
            }
            for idx, c in enumerate(chunks)
        ]
        with meta_file.open("w", encoding="utf-8") as fh:
            json.dump(chunk_metadata, fh, indent=2)

        print(f"[VectorImporter] Vector index built for {project_code} ({len(chunks)} vectors).")
        return str(faiss_file)

    def sync_all_projects(self):
        """
        Background job runner: Indexes vector DB for all projects.
        """
        project_codes = ['PRJ-001', 'PRJ-002', 'PRJ-003', 'PRJ-004', 'PRJ-005']
        for code in project_codes:
            try:
                self.index_project(code)
            except Exception as e:
                print(f"[VectorImporter Background Job Error for {code}] {e}")

    def query_project_vector_store(self, project_code: str, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Queries FAISS/numpy vector index specifically isolated for project_code.
        """
        safe_proj_code = project_code.replace("-", "_").lower()
        faiss_file = self.storage_dir / f"project_{safe_proj_code}_index.faiss"
        npy_file = self.storage_dir / f"project_{safe_proj_code}_vectors.npy"
        meta_file = self.storage_dir / f"project_{safe_proj_code}_metadata.json"

        if not meta_file.exists():
            self.index_project(project_code)

        if not meta_file.exists():
            return []

        try:
            with meta_file.open("r", encoding="utf-8") as fh:
                chunk_metadata = json.load(fh)

            if not chunk_metadata:
                return []

            query_vec = self.compute_embedding(query_text)

            if HAS_FAISS and faiss_file.exists():
                index = faiss.read_index(str(faiss_file))
                if index.ntotal == 0:
                    return []
                q_arr = np.array([query_vec], dtype=np.float32)
                k = min(top_k, index.ntotal)
                distances, indices = index.search(q_arr, k)

                results = []
                for i, idx_pos in enumerate(indices[0]):
                    if 0 <= idx_pos < len(chunk_metadata):
                        meta = chunk_metadata[idx_pos]
                        meta['distance'] = float(distances[0][i])
                        results.append(meta)
                return results
            elif npy_file.exists():
                vectors = np.load(str(npy_file))
                if len(vectors) == 0:
                    return []
                dists = np.linalg.norm(vectors - query_vec, axis=1)
                top_indices = np.argsort(dists)[:top_k]
                results = []
                for idx_pos in top_indices:
                    meta = chunk_metadata[idx_pos]
                    meta['distance'] = float(dists[idx_pos])
                    results.append(meta)
                return results
        except Exception as e:
            print(f"[VectorImporter Query Error] {e}")
            return []

