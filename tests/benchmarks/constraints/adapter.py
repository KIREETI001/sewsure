"""Single seam between the constraint suite and the feasibility engine.

Everything in this suite reaches the engine through ``evaluate_inputs``. If the
engine's entry point changes, this is the only file to touch.

Case files use the contract vocabulary (packages/contracts 1.0.0-draft.2, K1), which N1's
``sewsure_feasibility`` now shares, so this adapter only builds N1's types from case data.

Engine shape (N1, PR #12):

    evaluate(garment: Garment, measurements: Mapping[str, Measurement],
             recipe_id: str, params: Mapping[str, float]) -> ConstraintResult
"""
from __future__ import annotations

import importlib
import os
import sys
import math
from datetime import datetime
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


# Case files, the contract (K1 draft.2) and N1 share one vocabulary: dimension names, categories,
# fabric families and failure codes pass through unchanged. Only types are built here.

_DEFAULT_PANEL_MM = (520.0, 780.0)


def _parse_ts(ts: str | None) -> datetime | None:
    return None if ts is None else datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _value_mm(m: dict) -> float:
    """mm value of a case measurement. ``{"value", "unit"}`` is converted; a bare number is NaN."""
    if m.get("value_mm") is not None:
        return float(m["value_mm"])
    if m.get("unit") in _MM_PER_UNIT and m.get("value") is not None:
        return to_mm(m["value"], m["unit"])
    return math.nan  # no usable unit: the engine must refuse, not guess


def build_engine_args(inputs: dict, models) -> tuple:
    """Translate one case's inputs into N1 types. ``models`` is ``sewsure_feasibility``."""
    g, ms = inputs["garment"], inputs["measurements"]
    meas = {}
    for name, m in ms.items():
        meas[name] = models.Measurement(
            _value_mm(m), m["origin"], _parse_ts(m.get("confirmed_at")))
    length = meas["shoulder_to_hem"].value_mm if "shoulder_to_hem" in meas else math.nan
    width = meas["chest_flat_width"].value_mm if "chest_flat_width" in meas else math.nan
    w = width if math.isfinite(width) and width > 0 else _DEFAULT_PANEL_MM[0]
    h = length if math.isfinite(length) and length > 0 else _DEFAULT_PANEL_MM[1]
    margin = float(g.get("seam_margin_mm", 0))
    rect = lambda y0, y1: ((0.0, y0), (w, y0), (w, y1), (0.0, y1))  # noqa: E731
    # A seam margin widens each exclusion; N1 only tests intersection with the zone itself.
    zones = tuple(
        models.Zone(r["name"], r["name"], rect(r["from_shoulder_mm"] - margin, r["to_shoulder_mm"] + margin))
        for r in g.get("prohibited_regions", []))
    panel = models.FabricPanel("case", models.Side.BACK, rect(0.0, h), prohibited_regions=zones)
    garment = models.Garment("case", g["category"], g["fabric_family"], (panel,))
    return garment, meas, inputs["recipe_id"], dict(inputs["params"])


def _status_of(raw: Any) -> str | None:
    s = getattr(raw, "status", None)
    return None if s is None else str(getattr(s, "value", s))


def _codes_of(raw: Any) -> list[str]:
    codes = (str(getattr(c, "value", c)) for c in (getattr(raw, "failure_codes", None) or ()))
    return sorted(set(codes))


def evaluate_inputs(inputs: dict) -> Outcome:
    """Run one set of case inputs through the engine. Raises EngineUnavailable if it is missing.

    An exception from inside the engine is reported as indeterminate, never as a pass.
    """
    fn = load_engine()
    try:
        models = importlib.import_module(fn.__module__.split(".")[0])
        raw = fn(*build_engine_args(inputs, models))
    except Exception as exc:  # noqa: BLE001 - engine failures are data for the report
        return Outcome(None, error=f"{type(exc).__name__}: {exc}")
    return Outcome(_status_of(raw), _codes_of(raw), raw=raw)
