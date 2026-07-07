import pytest

from app.agents.phantom_insight import generate_insight_card
from app.core.agent_runtime import FakeAgentRuntime


@pytest.mark.asyncio
async def test_generate_insight_card_parses_structured_output():
    canned = (
        "INSIGHT: O lead visualizou a proposta e parou de responder após o preço.\n"
        "RECOMENDACAO: Ligação humana focando na flexibilidade do Afterpay."
    )
    runtime = FakeAgentRuntime(canned_response=canned)

    card = await generate_insight_card(
        lead_id="usr_123",
        context_chunks=["Trecho do funil oficial sobre o modelo Afterpay."],
        situation="Lead parou de responder 8 horas após ver o preço.",
        runtime=runtime,
    )

    assert card.lead_id == "usr_123"
    assert "Afterpay" in card.recommendation
    assert "parou de responder" in card.insight
