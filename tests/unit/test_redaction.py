"""Tests for PII redaction (SECURITY-03, BR-11)."""

from mini_aip.domain.ontology import DataType, ObjectType, PiiRedactor, PropertyType


def _type():
    return ObjectType(
        name="Customer",
        properties=(
            PropertyType(name="id", data_type=DataType.STRING, required=True),
            PropertyType(name="ssn", data_type=DataType.STRING, is_pii=True),
            PropertyType(name="name", data_type=DataType.STRING),
        ),
    )


def test_pii_is_masked_non_pii_preserved():
    ot = _type()
    props = {"id": "c1", "ssn": "999-88-7777", "name": "Alice"}
    out = PiiRedactor.redact(ot, props)
    assert out["ssn"] == "[REDACTED]"
    assert out["id"] == "c1"
    assert out["name"] == "Alice"
    assert "999-88-7777" not in str(out)


def test_redact_for_log_shape():
    ot = _type()
    out = PiiRedactor.redact_for_log(ot, "c1", {"id": "c1", "ssn": "x"})
    assert out["object_type"] == "Customer"
    assert out["id"] == "c1"
    assert out["properties"]["ssn"] == "[REDACTED]"
