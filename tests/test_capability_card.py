from cap.core import build_extension_namespace
from cap.core.capability_card import (
    CapabilityAuthentication,
    CapabilityCard,
    CapabilityExtensionNamespace,
    CapabilityGraphMetadata,
    CapabilitySupportedVerbs,
)


def test_extension_namespace_supports_additional_result_fields() -> None:
    namespace = build_extension_namespace(
        schema_url="https://abel.ai/cap/extensions/abel/v1.json",
        verbs=["extensions.abel.observe_predict_resolved_time"],
        additional_params={"graph.paths": {"include_edge_signs": "boolean"}},
        additional_result_fields={
            "extensions.abel.observe_predict_resolved_time": {"resolved_target_time": "string"}
        },
        notes=["abel-owned"],
    )

    assert isinstance(namespace, CapabilityExtensionNamespace)
    assert namespace.model_dump() == {
        "schema_url": "https://abel.ai/cap/extensions/abel/v1.json",
        "verbs": ["extensions.abel.observe_predict_resolved_time"],
        "additional_params": {"graph.paths": {"include_edge_signs": "boolean"}},
        "additional_result_fields": {
            "extensions.abel.observe_predict_resolved_time": {"resolved_target_time": "string"}
        },
        "notes": ["abel-owned"],
    }


def test_capability_authentication_accepts_oauth2() -> None:
    auth = CapabilityAuthentication.model_validate(
        {
            "type": "oauth2",
            "details": {"authorization_url": "https://example.com/oauth/authorize"},
        }
    )

    assert auth.type == "oauth2"


def test_capability_card_compact_dump_omits_empty_optional_groups() -> None:
    card = CapabilityCard(
        name="Example CAP Server",
        description="Compact capability card example.",
        endpoint="https://example.com/cap",
        conformance_level=1,
        conformance_name="Observe",
        supported_verbs=CapabilitySupportedVerbs(
            core=["meta.capabilities", "meta.methods", "observe.predict"],
        ),
        assumptions=["stationarity"],
        reasoning_modes_supported=["observational_prediction"],
        graph=CapabilityGraphMetadata(
            domains=["operations"],
            graph_representation="time_lagged_dag",
        ),
        authentication=CapabilityAuthentication(type="none"),
        extensions={
            "abel.stateful": build_extension_namespace(
                schema_url="https://abel.ai/cap/extensions/abel/v1.json",
                verbs=["extensions.abel.stateful.search_prepare"],
            )
        },
    )

    dumped = card.model_dump_compact(by_alias=True)

    assert dumped["supported_verbs"] == {
        "core": ["meta.capabilities", "meta.methods", "observe.predict"]
    }
    assert dumped["extensions"]["abel.stateful"] == {
        "schema_url": "https://abel.ai/cap/extensions/abel/v1.json",
        "verbs": ["extensions.abel.stateful.search_prepare"],
    }
    assert "access_tiers" not in dumped
    assert "bindings" not in dumped
    assert "disclosure_policy" not in dumped
