"""Extração de texto e chunking recursivo para o Funil Oficial Ativo
(Adendo V2.1, secao 3.1: "Motor de Chunking Recursivo: Divisão em Blocos
Semânticos Sobrepostos").
"""
import io

from docx import Document
from pypdf import PdfReader

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def extract_text(filename: str, content: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if lower.endswith(".docx"):
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    # .txt, .md e qualquer outro texto plano
    return content.decode("utf-8", errors="ignore")


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Divide em blocos sobrepostos por caracteres, respeitando quebras de
    parágrafo quando possível. Simples e determinístico — suficiente para a
    Fase 1; um chunker semântico mais sofisticado pode substituir isto depois
    sem alterar o restante do pipeline.
    """
    cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        chunks.append(cleaned[start:end])
        if end == len(cleaned):
            break
        start = end - overlap
    return chunks
