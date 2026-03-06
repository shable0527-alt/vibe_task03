from __future__ import annotations

import chromadb
from openai import OpenAI

from config import Config
from chunkers.text_chunker import Chunk
from utils.logger import get_logger

logger = get_logger(__name__)


class ChromaStore:
    """ChromaDB vector store with OpenAI embeddings."""

    def __init__(
        self,
        persist_dir: str | None = None,
        collection_name: str | None = None,
    ):
        persist_dir = persist_dir or Config.CHROMA_PERSIST_DIR
        collection_name = collection_name or Config.CHROMA_COLLECTION_NAME

        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._openai = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_BASE_URL,
        )
        logger.info(
            f"ChromaDB initialized: {persist_dir}/{collection_name} "
            f"({self._collection.count()} existing documents)"
        )

    def add_chunks(self, chunks: list[Chunk], batch_size: int = 50) -> int:
        """Embed and store chunks into ChromaDB. Returns count of added documents."""
        if not chunks:
            return 0

        added = 0
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            texts = [c.text for c in batch]
            embeddings = self._embed(texts)

            ids = []
            metadatas = []
            documents = []

            for chunk, emb in zip(batch, embeddings):
                doc_id = f"{chunk.metadata.get('source_file', 'unknown')}_{chunk.chunk_index}"
                meta = {
                    **chunk.metadata,
                    "category": chunk.category,
                    "keywords": ", ".join(chunk.keywords) if chunk.keywords else "",
                    "summary": chunk.summary,
                    "chunk_index": chunk.chunk_index,
                }
                ids.append(doc_id)
                metadatas.append(meta)
                documents.append(chunk.text)

            self._collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents,
            )
            added += len(batch)
            logger.info(f"Stored {added}/{len(chunks)} chunks")

        return added

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_category: str | None = None,
    ) -> list[dict]:
        """Search the knowledge base for relevant chunks."""
        query_embedding = self._embed([query])[0]

        where = None
        if filter_category:
            where = {"category": filter_category}

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        if results["documents"] and results["documents"][0]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                hits.append(
                    {
                        "text": doc,
                        "metadata": meta,
                        "score": 1 - dist,  # cosine similarity
                    }
                )
        return hits

    def get_stats(self) -> dict:
        """Return collection statistics."""
        count = self._collection.count()
        return {
            "total_documents": count,
            "collection_name": self._collection.name,
        }

    def delete_by_source(self, source_file: str) -> int:
        """Delete all chunks from a specific source file."""
        # Get all IDs matching the source file
        results = self._collection.get(
            where={"source_file": source_file},
            include=[],
        )
        if results["ids"]:
            self._collection.delete(ids=results["ids"])
            count = len(results["ids"])
            logger.info(f"Deleted {count} chunks from '{source_file}'")
            return count
        return 0

    def _embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using OpenAI API."""
        resp = self._openai.embeddings.create(
            model=Config.EMBEDDING_MODEL,
            input=texts,
        )
        return [item.embedding for item in resp.data]
