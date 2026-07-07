"""Agente PHANTOM — motor de insights restrito.

Decisão registrada no plano da Fase 1: PHANTOM NUNCA fala diretamente com o
lead, nunca escreve no CRM, nunca altera valores ou scripts. Sua única saída
é um "Insight Card" estruturado para um operador humano decidir o que fazer
(Especificação V2 Complementar, secao 4.2: "Seu canal de saída operacional é
estritamente a geração de cartões de recomendação (Insight Cards)").
"""
import uuid
from dataclasses import dataclass

from app.core.agent_runtime import AgentRuntimePort

PHANTOM_SYSTEM_PROMPT = """\
Você é PHANTOM, o motor de insights comerciais do ORION OS.

REGRAS ABSOLUTAS (violar qualquer uma delas é uma falha crítica):
- Você NUNCA envia mensagens diretamente para o lead.
- Você NUNCA atualiza o status do CRM diretamente.
- Você NUNCA altera valores, prazos ou condições contratuais.
- Você NUNCA aprova, executa ou sugere qualquer movimentação financeira.
- Sua única função é analisar o contexto fornecido e gerar uma recomendação
  objetiva para um operador humano, que decide o que fazer.

Responda SEMPRE no formato:
INSIGHT: <observação objetiva sobre o padrão comportamental do lead>
RECOMENDACAO: <ação sugerida para o operador humano>
"""


@dataclass
class InsightCard:
    card_id: str
    lead_id: str
    insight: str
    recommendation: str
    raw_model_output: str


async def generate_insight_card(
    *, lead_id: str, context_chunks: list[str], situation: str, runtime: AgentRuntimePort
) -> InsightCard:
    result = await runtime.run(
        agent_identifier="phantom",
        system_prompt=PHANTOM_SYSTEM_PROMPT,
        context_chunks=context_chunks,
        user_message=situation,
        temperature=0.3,
    )

    insight = ""
    recommendation = ""
    for line in result.generated_text_output.splitlines():
        if line.upper().startswith("INSIGHT:"):
            insight = line.split(":", 1)[1].strip()
        elif line.upper().startswith("RECOMENDACAO:") or line.upper().startswith("RECOMENDAÇÃO:"):
            recommendation = line.split(":", 1)[1].strip()

    return InsightCard(
        card_id=str(uuid.uuid4()),
        lead_id=lead_id,
        insight=insight or result.generated_text_output,
        recommendation=recommendation,
        raw_model_output=result.generated_text_output,
    )
