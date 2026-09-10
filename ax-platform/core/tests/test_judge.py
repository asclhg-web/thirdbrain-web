"""M6 판단 — 카드 검증기·인용 검증기 규율."""
import pytest

from axp.judge import assembler, cards


def _valid_card():
    return {"kind": "demand_forecast", "agent": "t", "proposal": "p",
            "values": [{"name": "n", "value": 10, "source": "fact_sales"}],
            "evidence": {"kind": "dims", "dims": {"product_id": "P-X"}},
            "approver": "a"}


def test_card_without_evidence_rejected(tmp_db):
    c = _valid_card()
    c["evidence"] = {}
    with pytest.raises(cards.CardValidationError):
        cards.create(c)


def test_card_value_without_source_rejected(tmp_db):
    c = _valid_card()
    c["values"][0].pop("source")
    with pytest.raises(cards.CardValidationError):
        cards.create(c)


def test_card_roundtrip(tmp_db):
    cid = cards.create(_valid_card())
    got = cards.get(cid)
    assert got["status"] == "proposed" and got["values"][0]["value"] == 10


def test_uncited_sentence_blocked():
    with pytest.raises(assembler.CitationError):
        assembler.verify_citations("불량이 늘었다", {"hits": []})


def test_fabricated_number_blocked():
    with pytest.raises(assembler.CitationError):
        assembler.verify_citations("판매는 999개였다 [근거: x]", {"hits": [{"v": 10}]})


def test_percent_rendering_allowed():
    assembler.verify_citations("확신도 88%입니다 [근거: Rule:1]",
                               {"hits": [{"confidence": 0.875}]})
