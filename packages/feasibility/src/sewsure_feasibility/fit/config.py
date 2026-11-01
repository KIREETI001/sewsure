"""Garment-specific ease ranges, loaded from ``ease_ranges.json``.

The file is PROVISIONAL until a human approves it (``approved_by`` set). While provisional every
assessment carries a warning saying so. Each value carries its own ``source`` and
``source_checked`` flag. Lengths are millimetres.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from typing import Any, cast


@dataclass(frozen=True)
class SourcedValue:
    value_mm: float
    source: str
    source_checked: bool


@dataclass(frozen=True)
class EaseProfile:
    """Ease bands for one stretch family. A value is in band X when ``ease < X_below_mm``."""

    name: str
    garment_types: tuple[str, ...]
    uncertainty: SourcedValue
    insufficient_below: SourcedValue
    close_below: SourcedValue
    regular_below: SourcedValue
    relaxed_below: SourcedValue

    def thresholds_mm(self) -> tuple[float, float, float, float]:
        return (
            self.insufficient_below.value_mm,
            self.close_below.value_mm,
            self.regular_below.value_mm,
            self.relaxed_below.value_mm,
        )


@dataclass(frozen=True)
class EaseConfig:
    status: str
    approved_by: str | None
    measurement: str
    profiles: dict[str, EaseProfile]

    @property
    def provisional(self) -> bool:
        return self.status != "approved" or not self.approved_by

    def profile_for_garment_type(self, garment_type: str | None) -> EaseProfile | None:
        """Fail closed: an unknown or missing garment type has no profile."""
        for profile in self.profiles.values():
            if garment_type in profile.garment_types:
                return profile
        return None


def _sourced(raw: Any, where: str) -> SourcedValue:
    d = cast("dict[str, Any]", raw)
    source = str(d.get("source", "")).strip()
    if not source:
        raise ValueError(f"{where}: every ease value needs a source")
    value = d["value"]
    if isinstance(value, bool) or not isinstance(value, int | float) or value < 0:
        raise ValueError(f"{where}: value must be a non-negative number of mm")
    return SourcedValue(float(value), source, bool(d.get("source_checked", False)))


def parse_config(raw: dict[str, Any]) -> EaseConfig:
    profiles: dict[str, EaseProfile] = {}
    for name, p in cast("dict[str, dict[str, Any]]", raw["profiles"]).items():
        bands = cast("dict[str, Any]", p["bands"])
        profile = EaseProfile(
            name=name,
            garment_types=tuple(cast("list[str]", p["garment_types"])),
            uncertainty=_sourced(p["uncertainty_mm"], f"{name}.uncertainty_mm"),
            insufficient_below=_sourced(bands["insufficient_below_mm"], f"{name}.insufficient"),
            close_below=_sourced(bands["close_below_mm"], f"{name}.close"),
            regular_below=_sourced(bands["regular_below_mm"], f"{name}.regular"),
            relaxed_below=_sourced(bands["relaxed_below_mm"], f"{name}.relaxed"),
        )
        t = profile.thresholds_mm()
        if list(t) != sorted(t) or len(set(t)) != len(t):
            raise ValueError(f"{name}: band thresholds must be strictly increasing")
        profiles[name] = profile
    return EaseConfig(
        status=str(raw["status"]),
        approved_by=cast("str | None", raw.get("approved_by")),
        measurement=str(raw["measurement"]),
        profiles=profiles,
    )


def load_config() -> EaseConfig:
    text = (
        resources.files("sewsure_feasibility.fit").joinpath("ease_ranges.json").read_text("utf-8")
    )
    return parse_config(cast("dict[str, Any]", json.loads(text)))
