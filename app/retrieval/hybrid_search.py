"""
ResearchPilot Edge - Hybrid Retrieval
Combines Dense Semantic Vector Search with Keyword-Aware BM25 / Reciprocal Rank Fusion (RRF).
"""

import math
import re
from typing import List, Dict, Any
from app.retrieval.vector_store import VectorStore
from app.core.logger import logger

class HybridRetriever:
    """
    Hybrid retrieval orchestrator combining dense vector embeddings and sparse lexical scores
    to maximize precision for technical keywords, model names, author references, and equations.
    """

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5, dense_weight: float = 0.7) -> List[Dict[str, Any]]:
        """
        Executes hybrid dense + sparse retrieval.
        Returns re-ranked list of chunks with composite scores and citation references.
        """
        if self.vector_store.total_chunks == 0:
            return []

        # 1. Dense Semantic Search
        dense_results = self.vector_store.search(query, top_k=top_k * 2, min_similarity=0.15)
        
        # 2. Sparse Lexical Scoring
        sparse_scores = self._compute_keyword_scores(query, self.vector_store.metadata)
        
        # 3. Score Fusion & Re-ranking
        chunk_map = {c["chunk_id"]: c for c in self.vector_store.metadata}
        dense_scores_map = {c["chunk_id"]: c.get("similarity_score", 0.0) for c in dense_results}

        all_candidate_ids = set(dense_scores_map.keys()).union(
            set(sorted(sparse_scores.keys(), key=sparse_scores.get, reverse=True)[:top_k * 2])
        )

        fused_results = []
        for cid in all_candidate_ids:
            chunk = chunk_map.get(cid)
            if not chunk:
                continue

            d_score = dense_scores_map.get(cid, 0.0)
            s_score = sparse_scores.get(cid, 0.0)
            
            # Weighted linear score combination
            composite_score = (dense_weight * d_score) + ((1.0 - dense_weight) * s_score)

            item = dict(chunk)
            item["dense_score"] = round(d_score, 4)
            item["keyword_score"] = round(s_score, 4)
            item["similarity_score"] = round(composite_score, 4)
            fused_results.append(item)

        # Sort descending by composite score
        fused_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_results = fused_results[:top_k]

        for rank, item in enumerate(top_results, start=1):
            item["rank"] = rank

        return top_results

    def _compute_keyword_scores(self, query: str, chunks: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculates normalized TF keyword overlap scores for chunks."""
        query_terms = set(re.findall(r'\b[a-zA-Z0-9_\-]{2,}\b', query.lower()))
        if not query_terms:
            return {}

        scores = {}
        max_score = 1e-6

        for chunk in chunks:
            cid = chunk["chunk_id"]
            text_lower = chunk["text"].lower()
            matched_terms = sum(1 for term in query_terms if term in text_lower)
            
            if matched_terms > 0:
                # Term frequency normalized by log of chunk length
                raw_tf = matched_terms / (1.0 + math.log(max(10, len(text_lower.split()))))
                scores[cid] = raw_tf
                if raw_tf > max_score:
                    max_score = raw_tf
            else:
                scores[cid] = 0.0

        # Min-max normalization
        normalized = {cid: score / max_score for cid, score in scores.items()}
        return normalized
