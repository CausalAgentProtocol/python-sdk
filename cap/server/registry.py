from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import re
from typing import Any, Literal, Mapping

from pydantic import BaseModel

from cap.server.responses import CAPHandlerSuccessSpec
from cap.server.contracts import CAPVerbContract

_CORE_VERB_PATTERN = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+$")
_EXTENSION_NAMESPACE_PATTERN = re.compile(r"^[a-z0-9_]+$")
_EXTENSION_NAME_PATTERN = re.compile(r"^[a-z0-9_]+$")
CAPHandlerSurface = Literal["core", "convenience", "extension"]
CAPDispatchHandler = Callable[
    [BaseModel, Any],
    dict[str, Any] | CAPHandlerSuccessSpec | Awaitable[dict[str, Any] | CAPHandlerSuccessSpec],
]


@dataclass(frozen=True)
class DispatchSpec:
    request_model: type[BaseModel]
    response_model: type[BaseModel]
    surface: CAPHandlerSurface
    handler: CAPDispatchHandler


class CAPVerbRegistry:
    def __init__(self, specs: Mapping[str, DispatchSpec] | None = None) -> None:
        self._specs: dict[str, DispatchSpec] = dict(specs or {})

    def core(
        self,
        contract_or_verb: CAPVerbContract | str,
        *,
        request_model: type[BaseModel] | None = None,
        response_model: type[BaseModel] | None = None,
        surface: CAPHandlerSurface = "core",
    ) -> Callable[
        [CAPDispatchHandler],
        CAPDispatchHandler,
    ]:
        def _register(handler: CAPDispatchHandler) -> CAPDispatchHandler:
            if isinstance(contract_or_verb, CAPVerbContract):
                self.register_core_contract(
                    contract_or_verb,
                    surface=surface,
                    handler=handler,
                )
            else:
                if request_model is None or response_model is None:
                    raise ValueError(
                        "Core registry decorator needs request_model and response_model when using a raw verb."
                    )
                self.register_core_verb(
                    contract_or_verb,
                    request_model=request_model,
                    response_model=response_model,
                    surface=surface,
                    handler=handler,
                )
            return handler

        return _register

    def extension(
        self,
        *,
        namespace: str,
        name: str,
        request_model: type[BaseModel],
        response_model: type[BaseModel],
    ) -> Callable[
        [CAPDispatchHandler],
        CAPDispatchHandler,
    ]:
        def _register(handler: CAPDispatchHandler) -> CAPDispatchHandler:
            self.register_extension(
                namespace=namespace,
                name=name,
                request_model=request_model,
                response_model=response_model,
                handler=handler,
            )
            return handler

        return _register

    def register(
        self,
        verb: str,
        *,
        request_model: type[BaseModel],
        response_model: type[BaseModel],
        surface: CAPHandlerSurface,
        handler: CAPDispatchHandler,
    ) -> None:
        self._specs[verb] = DispatchSpec(
            request_model=request_model,
            response_model=response_model,
            surface=surface,
            handler=handler,
        )

    def register_core_verb(
        self,
        verb: str,
        *,
        request_model: type[BaseModel],
        response_model: type[BaseModel],
        surface: CAPHandlerSurface = "core",
        handler: CAPDispatchHandler,
    ) -> None:
        if verb.startswith("extensions."):
            raise ValueError("Core CAP verbs cannot use the extensions.* namespace.")
        if not _CORE_VERB_PATTERN.fullmatch(verb):
            raise ValueError(f"Unsupported core CAP verb format: {verb}")
        if surface not in {"core", "convenience"}:
            raise ValueError(f"Unsupported core CAP surface: {surface}")
        self.register(
            verb,
            request_model=request_model,
            response_model=response_model,
            surface=surface,
            handler=handler,
        )

    def register_core_contract(
        self,
        contract: CAPVerbContract,
        *,
        surface: CAPHandlerSurface = "core",
        handler: CAPDispatchHandler,
    ) -> None:
        self.register_core_verb(
            contract.verb,
            request_model=contract.request_model,
            response_model=contract.response_model,
            surface=surface,
            handler=handler,
        )

    def register_extension(
        self,
        *,
        namespace: str,
        name: str,
        request_model: type[BaseModel],
        response_model: type[BaseModel],
        handler: CAPDispatchHandler,
    ) -> str:
        if not _EXTENSION_NAMESPACE_PATTERN.fullmatch(namespace):
            raise ValueError(f"Unsupported extension namespace: {namespace}")
        if not _EXTENSION_NAME_PATTERN.fullmatch(name):
            raise ValueError(f"Unsupported extension name: {name}")

        verb = f"extensions.{namespace}.{name}"
        self.register(
            verb,
            request_model=request_model,
            response_model=response_model,
            surface="extension",
            handler=handler,
        )
        return verb

    def get(self, verb: str) -> DispatchSpec | None:
        return self._specs.get(verb)

    @property
    def supported_verbs(self) -> list[str]:
        return sorted(self._specs.keys())

    def verbs_for_surface(self, surface: CAPHandlerSurface) -> list[str]:
        return [verb for verb, spec in self._specs.items() if spec.surface == surface]

    @property
    def extension_verbs_by_namespace(self) -> dict[str, list[str]]:
        namespaces: dict[str, list[str]] = {}
        for verb in self.verbs_for_surface("extension"):
            _, namespace, _ = verb.split(".", 2)
            namespaces.setdefault(namespace, []).append(verb)
        return namespaces
