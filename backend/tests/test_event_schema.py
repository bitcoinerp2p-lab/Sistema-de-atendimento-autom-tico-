from app.core.schemas import AbandonmentAlertIn, EventIn, FunnelUploadMetadata


def test_event_in_parses_v2_example_payload():
    payload = {
        "event_id": "a5d89f81-562b-4e4b-9d41-3b7c845b9112",
        "event_type": "OBJECAO_REGISTRADA",
        "timestamp": "2026-07-03T18:45:00Z",
        "actor_source": "agent_04_objection_mapper",
        "payload": {
            "lead_id": "usr_99214a1",
            "funnel_context": "funnel_2_qualification",
            "raw_text_friction": "O valor da parcela excede o orçamento do trimestre.",
            "objection_category": "FINANCEIRO_PRECO",
        },
    }

    event = EventIn.model_validate(payload)

    assert event.event_type == "OBJECAO_REGISTRADA"
    assert event.payload["lead_id"] == "usr_99214a1"


def test_funnel_upload_metadata_parses_v21_example():
    metadata = FunnelUploadMetadata.model_validate(
        {
            "uploaded_by": "usr_admin_01",
            "document_type": "MARKDOWN",
            "apply_immediately": True,
        }
    )
    assert metadata.document_type == "MARKDOWN"
    assert metadata.apply_immediately is True


def test_abandonment_alert_parses_v21_example():
    payload = {
        "alert_id": "alt_77218a-1102",
        "timestamp": "2026-07-03T19:10:15Z",
        "session_key": "chat:5511999999999",
        "telemetry_data": {
            "lead_id": "usr_5511999999999",
            "last_interaction_timestamp": "2026-07-03T11:10:15Z",
            "elapsed_seconds_without_response": 28800,
            "current_funnel_stage": "Funil_3_Oferta",
            "read_receipt_confirmed": True,
        },
    }

    alert = AbandonmentAlertIn.model_validate(payload)

    assert alert.telemetry_data.elapsed_seconds_without_response == 28800
    assert alert.telemetry_data.read_receipt_confirmed is True
