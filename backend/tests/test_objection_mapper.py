from app.agents.objection_mapper import classify_objection


def test_classifies_price_objection():
    assert classify_objection("O valor da parcela está caro demais para meu orçamento") == "FINANCEIRO_PRECO"


def test_classifies_deadline_objection():
    assert classify_objection("Preciso de mais tempo, o prazo está muito curto") == "PRAZO"


def test_classifies_trust_objection():
    assert classify_objection("Tenho dúvida se isso não é golpe") == "CONFIANCA"


def test_classifies_authority_objection():
    assert classify_objection("Preciso consultar minha esposa antes de decidir") == "AUTORIDADE"


def test_falls_back_to_outros():
    assert classify_objection("Só estou dando uma olhada, sem motivo específico") == "OUTROS"
