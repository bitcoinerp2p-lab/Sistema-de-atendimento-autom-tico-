"""Geração de embeddings — placeholder da Fase 1.

Os documentos de especificação assumem um modelo de embedding real (ex.:
text-embedding-3-small, 1536 dimensões). Como nenhuma credencial de provedor
de embeddings foi definida para este projeto ainda, esta função gera um vetor
determinístico via hashing (mesmo texto sempre gera o mesmo vetor), apenas
para permitir que o pipeline de chunking → embedding → indexação Qdrant seja
testado de ponta a ponta localmente.

Isto NÃO é uma representação semântica real — buscas por similaridade com
este placeholder não vão encontrar textos semanticamente parecidos, só
detectar duplicatas exatas. Antes de qualquer uso com leads reais, trocar
por um modelo de embedding de verdade (local ou via API).
"""
import hashlib

from app.core.config import get_settings

settings = get_settings()


def get_embedding(text: str) -> list[float]:
    dim = settings.qdrant_vector_size
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    # Expande o digest de 32 bytes para `dim` floats normalizados em [-1, 1].
    values: list[float] = []
    counter = 0
    while len(values) < dim:
        chunk = hashlib.sha256(digest + counter.to_bytes(4, "big")).digest()
        values.extend((b / 127.5) - 1.0 for b in chunk)
        counter += 1
    return values[:dim]
