"""Sistema técnico de reputação — funções puras (Especificação V2, secao 7).

Nesta fase, estas funções calculam o novo score dado um evento; o enforcement
automático em runtime (ex.: bloquear a saída de um agente em Red State antes
de chegar ao lead) fica para uma fase posterior, quando houver um agente de
conversação real rodando em produção. Por ora, isto é testável isoladamente
e pronto para ser plugado num pipeline de auditoria.
"""
from dataclasses import dataclass
from enum import Enum

REPUTATION_MAX = 10.0
REPUTATION_MIN = 0.0
REPUTATION_DEFAULT = 10.0

PRICE_HALLUCINATION_PENALTY = 1.5
RECOVERY_STEP = 0.1
RECOVERY_INTERACTIONS_REQUIRED = 50


class ReputationState(str, Enum):
    GREEN = "green"  # 9.0 a 10.0 — autonomia analítica completa
    YELLOW = "yellow"  # 7.0 a 8.9 — aviso de verificação, logs em DEBUG
    AMBER = "amber"  # 5.0 a 6.9 — saída forçada a passar por segundo agente validador
    RED = "red"  # abaixo de 5.0 — container desativado, ALERTA_OPERACIONAL crítico


def classify(score: float) -> ReputationState:
    if score >= 9.0:
        return ReputationState.GREEN
    if score >= 7.0:
        return ReputationState.YELLOW
    if score >= 5.0:
        return ReputationState.AMBER
    return ReputationState.RED


def apply_price_hallucination_penalty(score: float) -> float:
    """Gravidade média: desvio das informações oficiais de preço."""
    return max(REPUTATION_MIN, score - PRICE_HALLUCINATION_PENALTY)


def apply_scope_violation_penalty(_score: float) -> float:
    """Gravidade crítica: tentativa de ação financeira ou fora do escopo do
    agente. Zera o score imediatamente, independentemente do valor atual.
    """
    return REPUTATION_MIN


def apply_recovery(score: float, validated_interactions_since_last_update: int) -> float:
    """+0.1 para cada 50 interações validadas com sucesso, sem desvio."""
    steps = validated_interactions_since_last_update // RECOVERY_INTERACTIONS_REQUIRED
    return min(REPUTATION_MAX, score + steps * RECOVERY_STEP)


@dataclass(frozen=True)
class ReputationRestrictions:
    state: ReputationState
    requires_second_agent_review: bool
    debug_logging: bool
    container_disabled: bool


def restrictions_for(state: ReputationState) -> ReputationRestrictions:
    return ReputationRestrictions(
        state=state,
        requires_second_agent_review=state == ReputationState.AMBER,
        debug_logging=state in (ReputationState.YELLOW, ReputationState.AMBER, ReputationState.RED),
        container_disabled=state == ReputationState.RED,
    )
