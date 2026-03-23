from __future__ import annotations

from typing import Any, get_args, get_origin

from pydantic import BaseModel

from cap.core.contracts import CAPMethodDescriptor, CAPMethodFieldDescriptor
from cap.server.registry import CAPHandlerSurface


def build_method_descriptor(
    verb: str,
    *,
    request_model: type[BaseModel],
    response_model: type[BaseModel],
    surface: CAPHandlerSurface,
    description: str | None = None,
) -> CAPMethodDescriptor:
    params_model = _extract_model_type(request_model.model_fields.get("params"))
    result_model = _extract_model_type(response_model.model_fields.get("result"))
    return CAPMethodDescriptor(
        verb=verb,
        surface=surface,
        description=description,
        arguments=_build_field_descriptors(params_model),
        result_fields=_build_field_descriptors(result_model),
    )


def _extract_model_type(field: Any) -> type[BaseModel] | None:
    if field is None:
        return None
    annotation = field.annotation
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return annotation

    origin = get_origin(annotation)
    if origin is None:
        return None

    for candidate in get_args(annotation):
        if isinstance(candidate, type) and issubclass(candidate, BaseModel):
            return candidate
    return None


def _build_field_descriptors(model: type[BaseModel] | None) -> list[CAPMethodFieldDescriptor]:
    if model is None:
        return []

    schema = model.model_json_schema()
    required = set(schema.get("required", []))
    properties = schema.get("properties", {})
    return [
        CAPMethodFieldDescriptor(
            name=name,
            description=property_schema.get("description"),
            required=name in required,
            value_type=_schema_type(property_schema, schema),
            items_type=_items_type(property_schema, schema),
            enum=property_schema.get("enum"),
            default=property_schema.get("default"),
            min_length=property_schema.get("minLength"),
            max_length=property_schema.get("maxLength"),
            minimum=property_schema.get("minimum"),
            maximum=property_schema.get("maximum"),
            examples=property_schema.get("examples"),
        )
        for name, property_schema in properties.items()
    ]


def _schema_type(property_schema: dict[str, Any], root_schema: dict[str, Any]) -> str | None:
    resolved_schema = _resolve_schema(property_schema, root_schema)
    schema_type = resolved_schema.get("type")
    if isinstance(schema_type, str):
        return schema_type
    if isinstance(schema_type, list):
        return "|".join(str(item) for item in schema_type)
    if "enum" in resolved_schema:
        return "enum"
    return None


def _items_type(property_schema: dict[str, Any], root_schema: dict[str, Any]) -> str | None:
    resolved_schema = _resolve_schema(property_schema, root_schema)
    items = resolved_schema.get("items")
    if not isinstance(items, dict):
        return None

    resolved_items = _resolve_schema(items, root_schema)
    items_type = resolved_items.get("type")
    if isinstance(items_type, str):
        return items_type
    if isinstance(items_type, list):
        return "|".join(str(item) for item in items_type)
    if "properties" in resolved_items:
        return "object"
    return None


def _resolve_schema(schema: dict[str, Any], root_schema: dict[str, Any]) -> dict[str, Any]:
    ref = schema.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/$defs/"):
        return schema

    ref_name = ref.removeprefix("#/$defs/")
    defs = root_schema.get("$defs", {})
    resolved = defs.get(ref_name)
    if isinstance(resolved, dict):
        return resolved
    return schema
