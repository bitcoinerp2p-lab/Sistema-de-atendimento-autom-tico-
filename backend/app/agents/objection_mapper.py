"""Agente de Mapeamento de Objeções (Especificação V1, Agente 4).

Classificação por palavras-chave nesta fase — determinística e testável sem
depender de uma chamada de API. Uma classificação semântica via LLM pode
substituir `classify_objection` numa fase posterior sem alterar o resto do
pipeline (a assinatura da função é o contrato).
"""
import uuid
from dataclasses import dataclass

from app.services import qdrant_client
from app.services.embeddings import get_embedding

_KEYWORDS = {
    "FINANCEIRO_PRECO": ["preço", "preco", "caro", "valor", "parcela", "orçamento", "orcamento"],
    "PRAZO": ["prazo", "tempo", "demora", "quando", "urgente"],
    "CONFIANCA": ["confiança", "confianca", "golpe", "garantia", "seguro", "duvida", "dúvida"],
    "AUTORIDADE": ["decidir", "consultar", "sócio", "socio", "chefe", "esposa", "marido"],
}


@dataclass
class ObjectionRecord:
    point_id: str
    category: str
    raw_text: str


def classify_objection(raw_text: str) -> str:
    lowered = raw_text.lower()
    for category, keywords in _KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return category
    return "OUTROS"


def map_objection(*, lead_id: str, raw_text: str, funnel_stage: str) -> ObjectionRecord:
    category = classify_objection(raw_text)
    vector = get_embedding(raw_text)

    point_id = qdrant_client.upsert_point(
        qdrant_client.settings.qdrant_collection_objections,
        vector,
        payload={
            "lead_id": lead_id,
            "text": raw_text,
            "objection_category": category,
            "funnel_context": funnel_stage,
        },
        point_id=str(uuid.uuid4()),
    )

    return ObjectionRecord(point_id=point_id, category=category, raw_text=raw_text)
