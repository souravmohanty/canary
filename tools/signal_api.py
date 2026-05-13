from store.vector_store import get_store


def search_signals(query: str, n: int = 6) -> tuple[list[str], list[dict]]:
    """Retrieve the most relevant supplier signals for a query string."""
    return get_store().query(query, n=n)
