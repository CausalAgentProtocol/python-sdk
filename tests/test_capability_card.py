from cap.core import build_extension_namespace
from cap.core.capability_card import CapabilityExtensionNamespace


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
