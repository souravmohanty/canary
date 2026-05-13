import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd


class SignalStore:
    def __init__(self):
        self.client   = chromadb.Client()
        self.col      = self.client.get_or_create_collection("supplier_signals")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def ingest(self, df: pd.DataFrame) -> None:
        docs       = df["detail"].tolist()
        ids        = [str(i) for i in range(len(docs))]
        metas      = df[["supplier", "signal_type", "severity"]].to_dict("records")
        embeddings = self.embedder.encode(docs).tolist()
        self.col.add(documents=docs, embeddings=embeddings,
                     ids=ids, metadatas=metas)

    def query(self, text: str, n: int = 6) -> tuple[list[str], list[dict]]:
        emb     = self.embedder.encode([text]).tolist()
        results = self.col.query(query_embeddings=emb, n_results=n)
        return results["documents"][0], results["metadatas"][0]


_store: SignalStore | None = None


def get_store() -> SignalStore:
    global _store
    if _store is None:
        _store = SignalStore()
    return _store
