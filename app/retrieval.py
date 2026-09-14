from pathlib import Path
from dataclasses import dataclass
from typing import List
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import RetrievedChunk

KB_DIR = Path("data/knowledge_base")

@dataclass
class Chunk:
    source_title: str
    text: str

def _load_articles() -> List[Chunk]:
    chunks: List[Chunk] = []
    for path in sorted(KB_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        title = raw.splitlines()[0].lstrip("# ").strip() if raw else path.stem
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", raw) if p.strip()]
        for paragraph in paragraphs:
            chunks.append(Chunk(source_title=title, text=paragraph))
    if not chunks:
        raise FileNotFoundError("No knowledge base articles found in data/knowledge_base/")
    return chunks

class Retriever:
    def __init__(self) -> None:
        self._chunks = _load_articles()
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform([c.text for c in self._chunks])

    def search(self, query: str, top_k: int = 3) -> List[RetrievedChunk]:
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix).flatten()
        top_indices = scores.argsort()[::-1][:top_k]
        return [
            RetrievedChunk(
                source_title=self._chunks[i].source_title,
                text=self._chunks[i].text,
                score=float(scores[i]),
            )
            for i in top_indices
            if scores[i] > 0
        ]
