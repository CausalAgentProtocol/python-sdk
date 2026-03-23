from __future__ import annotations

from typing import Any, get_args, get_origin

from pydantic import BaseModel

from cap.core.contracts import CAPMethodDescriptor, CAPMethodFieldDescriptor, MetaMethodDetail
from cap.server.registry import CAPHandlerSurface


def build_method_descriptor(
    verb: str,
    *,
    request_model: type[BaseModel],
    response_model: type[BaseModel],
    surface: CAPHandlerSurface,
    description: str | None = None,
    detail: MetaMethodDetail = "compact",
    include_examples: bool = False,
) -> CAPMethodDescriptor:
    params_model = _extract_model_type(request_model.model_fields.get("params"))
    result_model = _extract_model_type(response_model.model_fields.get("result"))
    return CAPMethodDescriptor(
        verb=verb,
        surface=surface,
        description=description,
        arguments=_build_field_descriptors(
            params_model,
            detail=detail,
            include_examples=include_examples,
        ),
        result_fields=_build_field_descriptors(
            result_model,
            detail=detail,
            include_examples=include_examples,
        ),
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


def _build_field_descriptors(
    model: type[BaseModel] | None,
    *,
    detail: MetaMethodDetail,
    include_examples: bool,
) -> list[CAPMethodFieldDescriptor]:
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
            min_length=property_schema.get("minLength") if detail == "full" else None,
            max_length=property_schema.get("maxLength") if detail == "full" else None,
            minimum=property_schema.get("minimum") if detail == "full" else None,
            maximum=property_schema.get("maximum") if detail == "full" else None,
            examples=property_schema.get("examples") if include_examples else None,
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
    any_of = resolved_schema.get("anyOf")
    if isinstance(any_of, list):
        type_names = []
        for candidate in any_of:
            if not isinstance(candidate, dict):
                continue
            resolved_candidate = _resolve_schema(candidate, root_schema)
            candidate_type = resolved_candidate.get("type")
            if candidate_type == "null":
                continue
            if isinstance(candidate_type, str):
                type_names.append(candidate_type)
            elif isinstance(candidate_type, list):
                type_names.extend(
                    str(item) for item in candidate_type if item != "null"
                )
        if type_names:
            return "|".join(type_names)
    if "enum" in resolved_schema:
        return "enum"
    return None


def _items_type(property_schema: dict[str, Any], root_schema: dict[str, Any]) -> str | None:
    resolved_schema = _resolve_schema(property_schema, root_schema)
    items = resolved_schema.get("items")
    if not isinstance(items, dict):
        any_of = resolved_schema.get("anyOf")
        if isinstance(any_of, list):
            for candidate in any_of:
                if not isinstance(candidate, dict):
                    continue
                candidate_items = _items_type(candidate, root_schema)
                if candidate_items is not None:
                    return candidate_items
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
