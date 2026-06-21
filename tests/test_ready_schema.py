from cnsvintraday.data.ready_reader import REQUIRED_READY_FIELDS, ready_allows_observation, validate_ready_schema


def test_ready_schema_requires_all_contract_fields() -> None:
    ready_data = {"ready": True, "status": "PASS", "allowed_usage": {}}

    failures = validate_ready_schema(ready_data)

    assert failures == ["missing required ready field: trade_date"]


def test_ready_missing_required_field_blocks_observation() -> None:
    ready_data = {
        "trade_date": "20260622",
        "ready": True,
        "allowed_usage": {"can_run_intraday_forecast": True},
    }

    allowed, _warnings, failures = ready_allows_observation(ready_data)

    assert not allowed
    assert "missing required ready field: status" in failures


def test_required_ready_fields_are_stable() -> None:
    assert REQUIRED_READY_FIELDS == ("trade_date", "ready", "status", "allowed_usage")
