"""Single seam between the constraint suite and the feasibility engine.

Everything in this suite reaches the engine through ``evaluate_inputs``. If the
engine's entry point changes, this is the only file to touch.

Assumed engine shape (N1, packages/feasibility):

    evaluate(garment, measurements, recipe_id, params)
        -> object or dict with ``status`` and ``failure_codes``

``status`` may be a plain string or an Enum (``.value`` / ``.name`` is used).
"""
from __future__ import annotations

import importlib
import os
import sys
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
FEASIBILITY_DIR = REPO_ROOT / "packages" / "feasibility"
CANDIDATE_MODULES = ("sewsure_feasibility", "feasibility")

STATES = frozenset(
    {"IDEA_ONLY", "NEEDS_INPUT", "FAILED_CHECKS", "PASS_SUPPORTED_CHECKS", "SUPERSEDED"}
)
PASS = "PASS_SUPPORTED_CHECKS"

_MM_PER_UNIT = {"mm": Decimal(1), "cm": Decimal(10), "m": Decimal(1000)}


class EngineUnavailable(Exception):
    """The feasibility package could not be imported."""


@dataclass
class Outcome:
    """Normalised engine result. ``status`` is None when the engine gave no usable answer."""

    status: str | None
    failure_codes: list[str] = field(default_factory=list)
    error: str | None = None
    raw: Any = None

    @property
    def indeterminate(self) -> bool:
        return self.status not in STATES


def to_mm(value: float | int | str, unit: str) -> float:
    """Convert a length to mm. Decimal arithmetic so 78 cm and 780 mm are identical."""
    try:
        factor = _MM_PER_UNIT[unit]
    except KeyError:
        raise ValueError(f"unsupported unit: {unit!r}") from None
    return float(Decimal(str(value)) * factor)


_engine = None


def load_engine():
    """Return the engine's ``evaluate`` callable or raise EngineUnavailable."""
    global _engine
    if _engine is not None:
        return _engine
    names = [os.environ["SEWSURE_FEASIBILITY_MODULE"]] if os.environ.get("SEWSURE_FEASIBILITY_MODULE") else list(CANDIDATE_MODULES)
    for sub in ("src", ""):
        p = FEASIBILITY_DIR / sub if sub else FEASIBILITY_DIR
        if p.is_dir() and str(p) not in sys.path:
            sys.path.append(str(p))
    errors = []
    for name in names:
        try:
            mod = importlib.import_module(name)
        except ImportError as exc:
            errors.append(f"{name}: {exc}")
            continue
        fn = getattr(mod, "evaluate", None)
        if callable(fn):
            _engine = fn
            return fn
        errors.append(f"{name}: no callable 'evaluate'")
    raise EngineUnavailable(
        "feasibility engine not importable (tried " + "; ".join(errors) + "). "
        "Set SEWSURE_FEASIBILITY_MODULE or install packages/feasibility."
    )


def _normalise_measurement(m: Any) -> Any:
    """Convert any ``{"value": x, "unit": u}`` measurement to mm before it reaches the engine."""
    if isinstance(m, dict) and "value" in m and m.get("unit") in _MM_PER_UNIT:
        out = {k: v for k, v in m.items() if k not in ("value", "unit")}
        out["value_mm"] = to_mm(m["value"], m["unit"])
        return out
    return m


def _status_of(raw: Any) -> str | None:
    s = raw.get("status") if isinstance(raw, dict) else getattr(raw, "status", None)
    if s is None:
        return None
    return str(getattr(s, "value", None) or getattr(s, "name", None) or s)


def _codes_of(raw: Any) -> list[str]:
    codes = raw.get("failure_codes") if isinstance(raw, dict) else getattr(raw, "failure_codes", None)
    return sorted(str(getattr(c, "value", None) or getattr(c, "name", None) or c) for c in (codes or []))


def evaluate_inputs(inputs: dict) -> Outcome:
    """Run one set of case inputs through the engine. Raises EngineUnavailable if it is missing.

    An exception from inside the engine is reported as indeterminate, never as a pass.
    """
    fn = load_engine()
    measurements = {k: _normalise_measurement(v) for k, v in inputs["measurements"].items()}
    try:
        raw = fn(inputs["garment"], measurements, inputs["recipe_id"], inputs["params"])
    except Exception as exc:  # noqa: BLE001 - engine failures are data for the report
        return Outcome(None, error=f"{type(exc).__name__}: {exc}")
    return Outcome(_status_of(raw), _codes_of(raw), raw=raw)
