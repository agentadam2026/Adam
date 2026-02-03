"""Local embedding model for semantic search."""

from pathlib import Path
from typing import Optional

# Lazy-loaded model
_model = None
_model_name: str = ""


def get_model(model_name: str = "BAAI/bge-base-en-v1.5"):
    """Load the embedding model (lazy, cached)."""
    global _model, _model_name
    if _model is None or _model_name != model_name:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(model_name)
        _model_name = model_name
        print(f"Loaded embedding model: {model_name}")
    return _model


def embed_text(text: str, model_name: str = "BAAI/bge-base-en-v1.5") -> list[float]:
    """Embed a single text string. Returns a list of floats."""
    model = get_model(model_name)
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_texts(texts: list[str], model_name: str = "BAAI/bge-base-en-v1.5",
                batch_size: int = 32, show_progress: bool = True) -> list[list[float]]:
    """Embed multiple texts. Returns list of float lists."""
    model = get_model(model_name)
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=batch_size,
        show_progress_bar=show_progress,
    )
    return [e.tolist() for e in embeddings]


def get_dimensions(model_name: str = "BAAI/bge-base-en-v1.5") -> int:
    """Get the embedding dimensions for the model."""
    model = get_model(model_name)
    return model.get_sentence_embedding_dimension()
