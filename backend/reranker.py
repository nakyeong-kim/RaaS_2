# backend/reranker.py
from typing import List, Tuple
import os
import numpy as np

# Try to use sentence-transformers CrossEncoder (better quality)
try:
    from sentence_transformers import CrossEncoder
    _HAS_CROSS = True
except Exception:
    _HAS_CROSS = False

# Fallback: simple cosine scorer
from sklearn.metrics.pairwise import cosine_similarity

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.use_cross = _HAS_CROSS
        if self.use_cross:
            try:
                self.model = CrossEncoder(model_name)
            except Exception:
                self.use_cross = False
                self.model = None
        else:
            self.model = None

    def rerank(self, query: str, candidates: List[str], top_k: int = 5, embed_fn=None) -> List[Tuple[str, float]]:
        """
        - candidates: list of document chunks (texts)
        - embed_fn: optional function to get embedding of text (for cosine fallback)
        returns: list of (text, score) sorted desc
        """
        if len(candidates) == 0:
            return []

        if self.use_cross:
            # Cross-encoder expects pairs
            pairs = [[query, c] for c in candidates]
            scores = self.model.predict(pairs)  # higher = more relevant
            ranked_idx = np.argsort(scores)[::-1][:top_k]
            return [(candidates[i], float(scores[i])) for i in ranked_idx]
        else:
            # Fallback: use embed_fn (must be provided) to compute cosine similarity
            if embed_fn is None:
                # if no embed_fn, approximate by length heuristic
                scores = [len(c) for c in candidates]
                ranked_idx = np.argsort(scores)[::-1][:top_k]
                return [(candidates[i], float(scores[i])) for i in ranked_idx]
            q_emb = embed_fn(query)
            doc_embs = [embed_fn(c) for c in candidates]
            sims = cosine_similarity([q_emb], doc_embs)[0]
            ranked_idx = np.argsort(sims)[::-1][:top_k]
            return [(candidates[i], float(sims[i])) for i in ranked_idx]
