"""Replaceable local embedding providers for repository chunks and queries."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol


class EmbeddingProvider(Protocol):
    """Provider contract: encode texts into a 2D numeric vector array."""

    @property
    def dimension(self) -> int: ...

    @property
    def model_id(self) -> str: ...

    def embed(self, texts: Sequence[str]) -> object: ...


class HashEmbeddingProvider:
    """Stable feature-hash vectors for deterministic tests, not semantic search."""

    def __init__(self, dimension: int = 128):
        if dimension < 1:
            raise ValueError("Embedding dimension must be positive.")
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model_id(self) -> str:
        return f"feature-hash-v1:{self.dimension}"

    def embed(self, texts: Sequence[str]) -> np.ndarray:
        import numpy as np

        rows = np.zeros((len(texts), self.dimension), dtype=np.float32)
        for row, text in enumerate(texts):
            if not isinstance(text, str):
                raise ValueError("Embedding inputs must be strings.")
            for token in re.findall(r"[a-z][a-z0-9_]*", text.lower()):
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:8], "big") % self.dimension
                sign = 1.0 if digest[8] & 1 else -1.0
                rows[row, index] += sign
        return rows


class SentenceTransformerProvider:
    """Local Sentence Transformers adapter; refuses to download missing models."""

    def __init__(self, model_path: str, *, device: str | None = None):
        if not model_path or not model_path.strip():
            raise ValueError("A local Sentence Transformers model path is required.")
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError("Install the 'embeddings' extra to use Sentence Transformers.") from exc
        try:
            self._model = SentenceTransformer(model_path, device=device, local_files_only=True)
        except Exception as exc:
            raise RuntimeError(f"Could not load local embedding model at {model_path!r}: {exc}") from exc
        dimension_getter = getattr(self._model, "get_embedding_dimension", None)
        if not callable(dimension_getter):
            dimension_getter = getattr(self._model, "get_sentence_embedding_dimension", None)
        if not callable(dimension_getter):
            raise RuntimeError("The loaded embedding model does not expose its output dimension.")
        self._dimension = int(dimension_getter())
        self._model_id = str(Path(model_path).expanduser().resolve())

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model_id(self) -> str:
        return self._model_id

    def embed(self, texts: Sequence[str]) -> np.ndarray:
        import numpy as np

        if any(not isinstance(text, str) for text in texts):
            raise ValueError("Embedding inputs must be strings.")
        if not texts:
            return np.zeros((0, self.dimension), dtype=np.float32)
        return np.asarray(self._model.encode(list(texts), convert_to_numpy=True), dtype=np.float32)
