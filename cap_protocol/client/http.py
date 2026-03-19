from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Literal, TypeVar, cast

import httpx
from pydantic import BaseModel

from cap_protocol.core.builders import (
    build_graph_markov_blanket_request,
    build_graph_neighbors_request,
    build_graph_paths_request,
    build_intervene_do_request,
    build_meta_capabilities_request,
    build_observe_predict_request,
    build_traverse_children_request,
    build_traverse_parents_request,
)
from cap_protocol.core.contracts import (
    GraphMarkovBlanketResponse,
    GraphNeighborsResponse,
    GraphPathsResponse,
    InterveneDoResponse,
    MetaCapabilitiesResponse,
    ObservePredictResponse,
    TraverseResponse,
)
from cap_protocol.core.envelopes import (
    CAPGraphRef,
    CAPRequestBase,
    CAPRequestContext,
    CAPRequestOptions,
)
from cap_protocol.core.errors import CAPErrorBody, CAPErrorResponse, CAPHTTPError

ResponseT = TypeVar("ResponseT", bound=BaseModel)


class CAPClientGenericRequest(CAPRequestBase):
    verb: str
    params: dict[str, Any] | None = None


@dataclass(frozen=True)
class CAPClientVerbSpec:
    builder: Callable[..., CAPRequestBase]
    response_model: type[BaseModel]


DEFAULT_CLIENT_VERBS = {
    "meta.capabilities": CAPClientVerbSpec(
        builder=build_meta_capabilities_request,
        response_model=MetaCapabilitiesResponse,
    ),
    "graph.neighbors": CAPClientVerbSpec(
        builder=build_graph_neighbors_request,
        response_model=GraphNeighborsResponse,
    ),
    "graph.markov_blanket": CAPClientVerbSpec(
        builder=build_graph_markov_blanket_request,
        response_model=GraphMarkovBlanketResponse,
    ),
    "graph.paths": CAPClientVerbSpec(
        builder=build_graph_paths_request,
        response_model=GraphPathsResponse,
    ),
    "observe.predict": CAPClientVerbSpec(
        builder=build_observe_predict_request,
        response_model=ObservePredictResponse,
    ),
    "traverse.parents": CAPClientVerbSpec(
        builder=build_traverse_parents_request,
        response_model=TraverseResponse,
    ),
    "traverse.children": CAPClientVerbSpec(
        builder=build_traverse_children_request,
        response_model=TraverseResponse,
    ),
    "intervene.do": CAPClientVerbSpec(
        builder=build_intervene_do_request,
        response_model=InterveneDoResponse,
    ),
}


@dataclass(frozen=True)
class CAPClientRoutes:
    single_entry_path: str = "/api/v1/cap"

    def resolve(self, verb: str) -> str:
        return _normalize_path(self.single_entry_path)

    def resolve_verb(self, route: str) -> str:
        normalized_route = route.strip()
        if not normalized_route:
            raise ValueError("Route alias cannot be empty.")
        if "/" not in normalized_route:
            return normalized_route.strip(".")

        segments = [segment for segment in normalized_route.strip("/").split("/") if segment]
        if not segments:
            raise ValueError("Route alias cannot be empty.")
        return ".".join(segments)


class AsyncCAPClient:
    def __init__(
        self,
        base_url: str,
        *,
        routes: CAPClientRoutes | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._routes = routes or CAPClientRoutes()
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/") + "/",
            headers=dict(headers or {}),
            timeout=timeout,
            transport=transport,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def request(
        self,
        payload: CAPRequestBase,
        response_model: type[ResponseT],
        *,
        headers: Mapping[str, str] | None = None,
    ) -> ResponseT:
        verb = getattr(payload, "verb", None)
        if not isinstance(verb, str):
            raise ValueError("CAP request payload must expose a string verb.")

        response = await self._client.post(
            self._routes.resolve(verb),
            json=payload.model_dump(exclude_none=True),
            headers=dict(headers) if headers is not None else None,
        )
        if response.is_error:
            raise self._build_http_error(response)
        return response_model.model_validate(response.json())

    async def request_verb(
        self,
        verb: str,
        *,
        params: Mapping[str, Any] | BaseModel | None = None,
        graph_ref: CAPGraphRef | None = None,
        request_id: str | None = None,
        options: CAPRequestOptions | None = None,
        headers: Mapping[str, str] | None = None,
        response_model: type[ResponseT],
    ) -> ResponseT:
        payload_kwargs: dict[str, Any] = {
            "verb": verb,
            "request_id": request_id,
        }
        if params is not None:
            payload_kwargs["params"] = _normalize_params(params)
        if options is not None:
            payload_kwargs["options"] = options
        if graph_ref is not None:
            payload_kwargs["context"] = CAPRequestContext(graph_ref=graph_ref)
        payload = CAPClientGenericRequest(**payload_kwargs)
        return await self.request(payload, response_model, headers=headers)

    async def request_route(
        self,
        route: str,
        *,
        params: Mapping[str, Any] | BaseModel | None = None,
        graph_ref: CAPGraphRef | None = None,
        request_id: str | None = None,
        options: CAPRequestOptions | None = None,
        headers: Mapping[str, str] | None = None,
        response_model: type[ResponseT],
    ) -> ResponseT:
        verb = self._routes.resolve_verb(route)
        return await self.request_verb(
            verb,
            params=params,
            graph_ref=graph_ref,
            request_id=request_id,
            options=options,
            headers=headers,
            response_model=response_model,
        )

    async def meta_capabilities(
        self,
        *,
        request_id: str | None = None,
        options: CAPRequestOptions | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> MetaCapabilitiesResponse:
        payload = build_meta_capabilities_request(request_id=request_id, options=options)
        return await self.request(payload, MetaCapabilitiesResponse, headers=headers)

    async def graph_neighbors(
        self,
        *,
        node_id: str,
        scope: Literal["parents", "children"],
        max_neighbors: int = 10,
        graph_ref: CAPGraphRef | None = None,
        request_id: str | None = None,
        options: CAPRequestOptions | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> GraphNeighborsResponse:
        payload = build_graph_neighbors_request(
            node_id=node_id,
            scope=cast(Literal["parents", "children"], scope),
            max_neighbors=max_neighbors,
            graph_ref=graph_ref,
            request_id=request_id,
            options=options,
        )
        return await self.request(payload, GraphNeighborsResponse, headers=headers)

    async def graph_markov_blanket(
        self,
        *,
        node_id: str,
        max_neighbors: int = 10,
        graph_ref: CAPGraphRef | None = None,
        request_id: str | None = None,
        options: CAPRequestOptions | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> GraphMarkovBlanketResponse:
        payload = build_graph_markov_blanket_request(
            node_id=node_id,
            max_neighbors=max_neighbors,
            graph_ref=graph_ref,
            request_id=request_id,
            options=options,
        )
        return await self.request(payload, GraphMarkovBlanketResponse, headers=headers)

    async def graph_paths(
        self,
        *,
        source_node_id: str,
        target_node_id: str,
        max_paths: int = 3,
        graph_ref: CAPGraphRef | None = None,
        request_id: str | None = None,
        options: CAPRequestOptions | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> GraphPathsResponse:
        payload = build_graph_paths_request(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            max_paths=max_paths,
            graph_ref=graph_ref,
            request_id=request_id,
            options=options,
        )
        return await self.request(payload, GraphPathsResponse, headers=headers)

    async def traverse_parents(
        self,
        *,
        node_id: str,
        top_k: int = 10,
        graph_ref: CAPGraphRef | None = None,
        request_id: str | None = None,
        options: CAPRequestOptions | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> TraverseResponse:
        payload = build_traverse_parents_request(
            node_id=node_id,
            top_k=top_k,
            graph_ref=graph_ref,
            request_id=request_id,
            options=options,
        )
        return await self.request(payload, TraverseResponse, headers=headers)

    async def traverse_children(
        self,
        *,
        node_id: str,
        top_k: int = 10,
        graph_ref: CAPGraphRef | None = None,
        request_id: str | None = None,
        options: CAPRequestOptions | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> TraverseResponse:
        payload = build_traverse_children_request(
            node_id=node_id,
            top_k=top_k,
            graph_ref=graph_ref,
            request_id=request_id,
            options=options,
        )
        return await self.request(payload, TraverseResponse, headers=headers)

    async def observe_predict(
        self,
        *,
        target_node: str,
        graph_ref: CAPGraphRef | None = None,
        request_id: str | None = None,
        options: CAPRequestOptions | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> ObservePredictResponse:
        payload = build_observe_predict_request(
            target_node=target_node,
            graph_ref=graph_ref,
            request_id=request_id,
            options=options,
        )
        return await self.request(payload, ObservePredictResponse, headers=headers)

    async def intervene_do(
        self,
        *,
        treatment_node: str,
        treatment_value: float,
        outcome_node: str,
        graph_ref: CAPGraphRef | None = None,
        request_id: str | None = None,
        options: CAPRequestOptions | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> InterveneDoResponse:
        payload = build_intervene_do_request(
            treatment_node=treatment_node,
            treatment_value=treatment_value,
            outcome_node=outcome_node,
            graph_ref=graph_ref,
            request_id=request_id,
            options=options,
        )
        return await self.request(payload, InterveneDoResponse, headers=headers)

    @staticmethod
    def _build_http_error(response: httpx.Response) -> CAPHTTPError:
        response_payload: dict[str, Any] | None = None
        cap_error: CAPErrorBody | None = None
        message = response.text or f"CAP request failed with status {response.status_code}."

        try:
            payload = response.json()
        except ValueError:
            payload = None

        if isinstance(payload, dict):
            response_payload = payload
            try:
                cap_response = CAPErrorResponse.model_validate(payload)
            except Exception:
                cap_response = None
            if cap_response is not None:
                cap_error = cap_response.error
                message = cap_error.message

        return CAPHTTPError(
            status_code=response.status_code,
            message=message,
            cap_error=cap_error,
            response_payload=response_payload,
        )


def _normalize_path(path: str) -> str:
    return "/" + path.strip("/")


def _normalize_params(params: Mapping[str, Any] | BaseModel) -> dict[str, Any]:
    if isinstance(params, BaseModel):
        return params.model_dump(exclude_none=True)
    return dict(params)
