"""Persistent, traceable cosine vector index with optional FAISS acceleration."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from devmind.embeddings import EmbeddingProvider
from devmind.models import CodeChunk, Evidence

_FORMAT_VERSION = 1


class VectorIndex:
    """Embed chunks once and search by cosine similarity.

    FAISS is used when installed; otherwise exact NumPy search keeps the same
    result contract. Rows in the persisted matrix map directly to chunk IDs.
    """

    def __init__(self, chunks: list[CodeChunk], embedder: EmbeddingProvider):
        self.chunks = list(chunks)
        self.embedder = embedder
        texts = [_chunk_text(chunk) for chunk in self.chunks]
        vectors = embedder.embed(texts)
        self.vectors = _validate_vectors(vectors, len(self.chunks), embedder.dimension)
        self.vectors = _normalize(self.vectors)
        self._faiss_index = _make_faiss(self.vectors)

    @classmethod
    def _from_saved(cls, chunks: list[CodeChunk], vectors: np.ndarray, embedder: EmbeddingProvider) -> "VectorIndex":
        instance = cls.__new__(cls)
        instance.chunks = chunks
        instance.embedder = embedder
        instance.vectors = _normalize(_validate_vectors(vectors, len(chunks), embedder.dimension))
        instance._faiss_index = _make_faiss(instance.vectors)
        return instance

    def search(self, query: str, *, limit: int = 8) -> list[Evidence]:
        if limit < 1:
            raise ValueError("limit must be positive.")
        if not isinstance(query, str):
            raise ValueError("Query must be a string.")
        if not query.strip() or not self.chunks:
            return []
        import numpy as np

        query_vector = _validate_vectors(self.embedder.embed([query]), 1, self.embedder.dimension)
        query_vector = _normalize(query_vector)
        if not np.any(query_vector):
            return []
        if self._faiss_index is not None:
            scores, ids = self._faiss_index.search(query_vector, min(limit, len(self.chunks)))
            pairs = [(int(i), float(score)) for i, score in zip(ids[0], scores[0]) if i >= 0]
        else:
            scores = self.vectors @ query_vector[0]
            pairs = [(i, float(score)) for i, score in enumerate(scores)]
        pairs.sort(key=lambda pair: (-pair[1], self.chunks[pair[0]].path, self.chunks[pair[0]].start_line))
        return [Evidence(self.chunks[i], round(score, 6)) for i, score in pairs[:limit]]

    def save(self, directory: str | Path) -> Path:
        """Persist vectors and their ordered chunk metadata as safe JSON/NPY files."""
        target = Path(directory)
        target.mkdir(parents=True, exist_ok=True)
        vector_path = target / "vectors.npy"
        metadata_path = target / "metadata.json"
        vector_tmp = target / "vectors.npy.tmp"
        metadata_tmp = target / "metadata.json.tmp"
        import numpy as np

        with vector_tmp.open("wb") as stream:
            np.save(stream, self.vectors, allow_pickle=False)
        payload: dict[str, Any] = {
            "format_version": _FORMAT_VERSION,
            "dimension": self.embedder.dimension,
            "model_id": self.embedder.model_id,
            "metric": "cosine_similarity",
            "chunks": [_chunk_to_dict(chunk) for chunk in self.chunks],
        }
        metadata_tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(vector_tmp, vector_path)
        os.replace(metadata_tmp, metadata_path)
        return target

    @classmethod
    def load(cls, directory: str | Path, embedder: EmbeddingProvider) -> "VectorIndex":
        """Load a saved index; reject incompatible or malformed dimensions."""
        root = Path(directory)
        try:
            payload = json.loads((root / "metadata.json").read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Vector index metadata must be a JSON object.")
            if payload.get("format_version") != _FORMAT_VERSION:
                raise ValueError("Unsupported vector index format version.")
            if payload.get("dimension") != embedder.dimension:
                raise ValueError("Embedder dimension does not match the saved vector index.")
            if payload.get("model_id") != embedder.model_id:
                raise ValueError("Embedding model does not match the saved vector index.")
            chunks = [_chunk_from_dict(item) for item in payload["chunks"]]
            import numpy as np

            with (root / "vectors.npy").open("rb") as stream:
                vectors = np.load(stream, allow_pickle=False)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, AttributeError) as exc:
            raise ValueError(f"Could not load vector index at {root}: {exc}") from exc
        return cls._from_saved(chunks, vectors, embedder)


def _chunk_text(chunk: CodeChunk) -> str:
    return f"{chunk.path}\n{chunk.name}\n{chunk.kind}\n{chunk.content}"


def _validate_vectors(vectors: object, rows: int, dimension: int) -> object:
    import numpy as np

    array = np.asarray(vectors, dtype=np.float32)
    if array.shape != (rows, dimension):
        raise ValueError(f"Embedding output must have shape ({rows}, {dimension}); got {array.shape}.")
    if not np.isfinite(array).all():
        raise ValueError("Embedding output must contain only finite numbers.")
    return array


def _normalize(vectors: object) -> object:
    import numpy as np

    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return np.divide(vectors, norms, out=np.zeros_like(vectors), where=norms != 0)


def _make_faiss(vectors: np.ndarray) -> Any | None:
    import numpy as np

    if not len(vectors):
        return None
    try:
        import faiss
    except ImportError:
        return None
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(np.ascontiguousarray(vectors, dtype=np.float32))
    return index


def _chunk_to_dict(chunk: CodeChunk) -> dict[str, Any]:
    return {"path": chunk.path, "name": chunk.name, "kind": chunk.kind, "start_line": chunk.start_line, "end_line": chunk.end_line, "content": chunk.content}


def _chunk_from_dict(item: dict[str, Any]) -> CodeChunk:
    return CodeChunk(path=item["path"], name=item["name"], kind=item["kind"], start_line=int(item["start_line"]), end_line=int(item["end_line"]), content=item["content"])
