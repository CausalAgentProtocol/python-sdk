from cap.core import (
    ASSUMPTION_CAUSAL_SUFFICIENCY,
    ASSUMPTION_FAITHFULNESS,
    ASSUMPTION_LINEARITY,
    ASSUMPTION_NO_INSTANTANEOUS_EFFECTS,
    ASSUMPTION_NO_LATENT_CONFOUNDERS_ADDRESSED,
    MetaMethodsRequest,
    build_meta_methods_request,
)
from cap.core.disclosure import sanitize_fields


def test_core_re_exports() -> None:
    assert ASSUMPTION_CAUSAL_SUFFICIENCY == "causal_sufficiency"
    assert ASSUMPTION_FAITHFULNESS == "faithfulness"
    assert ASSUMPTION_LINEARITY == "linearity"
    assert ASSUMPTION_NO_INSTANTANEOUS_EFFECTS == "no_instantaneous_effects"
    assert (
        ASSUMPTION_NO_LATENT_CONFOUNDERS_ADDRESSED
        == "no_latent_confounders_addressed"
    )


def test_sanitize_fields_import() -> None:
    payload = {"keep": 1, "secret": 2, "nested": [{"secret": 3, "keep": 4}]}

    sanitized = sanitize_fields(payload, forbidden_fields={"secret"})

    assert sanitized == {"keep": 1, "nested": [{"keep": 4}]}


def test_meta_methods_exports() -> None:
    payload = build_meta_methods_request(request_id="req-methods")

    assert isinstance(payload, MetaMethodsRequest)
    assert payload.verb == "meta.methods"
