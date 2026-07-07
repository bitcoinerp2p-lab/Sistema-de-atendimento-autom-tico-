from app.core.reputation import (
    REPUTATION_MAX,
    REPUTATION_MIN,
    ReputationState,
    apply_price_hallucination_penalty,
    apply_recovery,
    apply_scope_violation_penalty,
    classify,
    restrictions_for,
)


def test_classify_boundaries():
    assert classify(10.0) == ReputationState.GREEN
    assert classify(9.0) == ReputationState.GREEN
    assert classify(8.9) == ReputationState.YELLOW
    assert classify(7.0) == ReputationState.YELLOW
    assert classify(6.9) == ReputationState.AMBER
    assert classify(5.0) == ReputationState.AMBER
    assert classify(4.9) == ReputationState.RED
    assert classify(0.0) == ReputationState.RED


def test_price_hallucination_penalty_subtracts_1_5():
    assert apply_price_hallucination_penalty(10.0) == 8.5
    assert apply_price_hallucination_penalty(1.0) == REPUTATION_MIN  # nunca fica negativo


def test_scope_violation_zeroes_score_regardless_of_current_value():
    assert apply_scope_violation_penalty(10.0) == REPUTATION_MIN
    assert apply_scope_violation_penalty(0.0) == REPUTATION_MIN


def test_recovery_requires_50_interactions_per_step():
    assert apply_recovery(5.0, validated_interactions_since_last_update=49) == 5.0
    assert apply_recovery(5.0, validated_interactions_since_last_update=50) == 5.1
    assert apply_recovery(5.0, validated_interactions_since_last_update=150) == 5.3


def test_recovery_never_exceeds_max():
    assert apply_recovery(9.95, validated_interactions_since_last_update=1000) == REPUTATION_MAX


def test_restrictions_for_each_state():
    green = restrictions_for(ReputationState.GREEN)
    assert not green.requires_second_agent_review
    assert not green.debug_logging
    assert not green.container_disabled

    amber = restrictions_for(ReputationState.AMBER)
    assert amber.requires_second_agent_review
    assert amber.debug_logging
    assert not amber.container_disabled

    red = restrictions_for(ReputationState.RED)
    assert red.container_disabled
