from dataclasses import dataclass
from typing import List
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from pathlib import Path

from .data_store import DEFAULT_DB_PATH, get_approved_articles, get_verified_resolutions
from .models import RetrievedChunk

@dataclass
class Chunk:
    source_title: str
    text: str
    source_type: str
    source_id: str


def _load_corpus(db_path: Path = DEFAULT_DB_PATH) -> List[Chunk]:
    chunks: List[Chunk] = []
    for article in get_approved_articles(db_path):
        raw = article["content"]
        title = article["title"]
        paragraphs = [
            p.strip()
            for p in re.split(r"\n\s*\n", raw)
            if p.strip() and not p.lstrip().startswith("#")
        ]
        for paragraph in paragraphs:
            chunks.append(
                Chunk(
                    source_title=title,
                    text=paragraph,
                    source_type="knowledge_article",
                    source_id=article["article_id"],
                )
            )
    for case in get_verified_resolutions(db_path):
        chunks.append(
            Chunk(
                source_title=f"Verified case {case['ticket_id']}: {case['subject']}",
                text=(
                    f"Problem: {case['description']}\n"
                    f"Category: {case['category']}\n"
                    f"Verified resolution: {case['resolution']}"
                ),
                source_type="verified_case",
                source_id=case["ticket_id"],
            )
        )
    if not chunks:
        raise FileNotFoundError("No approved articles or verified case resolutions were found.")
    return chunks


class Retriever:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        self._chunks = _load_corpus(self.db_path)
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform([c.text for c in self._chunks])

    def refresh(self) -> None:
        self._chunks = _load_corpus(self.db_path)
        self._matrix = self._vectorizer.fit_transform([c.text for c in self._chunks])

    def search(self, query: str, top_k: int = 3, min_score: float = 0.0) -> List[RetrievedChunk]:
        # Refreshing keeps newly human-verified resolutions available without retraining an LLM.
        self.refresh()
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix).flatten()
        candidates = scores.argsort()[::-1]
        results: List[RetrievedChunk] = []
        seen_sources: set[str] = set()
        for index in candidates:
            score = float(scores[index])
            chunk = self._chunks[index]
            if score < min_score or chunk.source_title in seen_sources:
                continue
            results.append(
                RetrievedChunk(
                    source_title=chunk.source_title,
                    text=chunk.text,
                    score=score,
                    source_type=chunk.source_type,
                    source_id=chunk.source_id,
                )
            )
            seen_sources.add(chunk.source_title)
            if len(results) >= top_k:
                break
        return results
