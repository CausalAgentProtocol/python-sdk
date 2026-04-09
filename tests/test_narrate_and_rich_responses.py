from cap.core import (
    InterveneDoResponse,
    NarrateResponse,
    NarrateRequest,
    ObservePredictResponse,
    build_narrate_request,
)


def test_build_narrate_request() -> None:
    payload = build_narrate_request(query="Why is NVDA moving?")

    assert isinstance(payload, NarrateRequest)
    assert payload.verb == "narrate"
    assert payload.params.query == "Why is NVDA moving?"


def test_observe_predict_response_preserves_extra_result_fields() -> None:
    payload = ObservePredictResponse.model_validate(
        {
            "cap_version": "0.3.0",
            "request_id": "req-1",
            "verb": "observe.predict",
            "status": "success",
            "result": {
                "target_node": "pub:NVDA:PREDICTION:gpu_demand",
                "prediction": 0.74,
                "drivers": ["pub:NVDA:FACT:cloud_capex"],
                "driver_details": [{"node_id": "pub:NVDA:FACT:cloud_capex"}],
                "summary": "extra fields should be ignored by the typed model",
            },
            "provenance": {
                "algorithm": "provider.predict",
                "graph_version": "news_graph_v1",
                "computation_time_ms": 12,
                "server_name": "test-server",
                "server_version": "0.1.0",
                "cap_spec_version": "0.3.0",
            },
        }
    )

    assert payload.result.target_node == "pub:NVDA:PREDICTION:gpu_demand"
    assert payload.result.prediction == 0.74
    assert payload.result.drivers == ["pub:NVDA:FACT:cloud_capex"]
    dumped = payload.model_dump(exclude_none=True)
    assert dumped["result"]["driver_details"] == [{"node_id": "pub:NVDA:FACT:cloud_capex"}]
    assert dumped["result"]["summary"] == "extra fields should be ignored by the typed model"


def test_narrate_response_accepts_minimum_success_payload() -> None:
    payload = NarrateResponse.model_validate(
        {
            "cap_version": "0.3.0",
            "request_id": "req-1",
            "verb": "narrate",
            "status": "success",
            "result": {"narrative": "Minimal narrative"},
        }
    )

    assert payload.result.narrative == "Minimal narrative"
    assert payload.provenance is None


def test_narrate_response_preserves_extra_result_fields() -> None:
    payload = NarrateResponse.model_validate(
        {
            "cap_version": "0.3.0",
            "request_id": "req-2",
            "verb": "narrate",
            "status": "success",
            "result": {
                "narrative": "Minimal narrative",
                "primary_node": {"node_id": "pub:NVDA:PREDICTION:gpu_demand"},
                "summary": "provider-specific detail",
            },
        }
    )

    dumped = payload.model_dump(exclude_none=True)
    assert dumped["result"]["primary_node"] == {"node_id": "pub:NVDA:PREDICTION:gpu_demand"}
    assert dumped["result"]["summary"] == "provider-specific detail"


def test_intervene_do_response_preserves_extra_result_fields() -> None:
    payload = InterveneDoResponse.model_validate(
        {
            "cap_version": "0.3.0",
            "request_id": "req-3",
            "verb": "intervene.do",
            "status": "success",
            "result": {
                "outcome_node": "pub:NVDA:PREDICTION:gpu_demand",
                "effect": 0.18,
                "reasoning_mode": "graph_propagation",
                "identification_status": "not_formally_identified",
                "assumptions": [],
                "mapping_type": "query_local_bridge",
                "direction": "increase",
            },
            "provenance": {
                "algorithm": "provider.intervene",
                "graph_version": "news_graph_v1",
                "computation_time_ms": 14,
                "server_name": "test-server",
                "server_version": "0.1.0",
                "cap_spec_version": "0.3.0",
            },
        }
    )

    dumped = payload.model_dump(exclude_none=True)
    assert dumped["result"]["mapping_type"] == "query_local_bridge"
    assert dumped["result"]["direction"] == "increase"
