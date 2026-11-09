"""Garment profile models for garment-aware transformation feasibility.

All garment measurements are stored in millimetres.
The existing Garment and Measurement classes are reused.
"""

from __future__ import annotations

import math
import types
from collections.abc import Mapping
from dataclasses import dataclass

from sewsure_feasibility.models import Garment, Measurement

# Accepted garment measurements for SewSure's first iteration.
GARMENT_MEASUREMENT_KEYS = frozenset(
    {
        "shoulder_to_hem",
        "chest_flat_width",
        "waist_flat_width",
        "hem_flat_width",
        "shoulder_width",
        "sleeve_length",
        "sleeve_flat_width",
        "upper_arm_flat_width",
        "cuff_circumference",
        "collar_length",
    }
)


@dataclass(frozen=True)
class GarmentProfile:
    """Stores the physical garment and its manually measured dimensions."""

    profile_id: str
    garment: Garment
    measurements: Mapping[str, Measurement]

    def __post_init__(self) -> None:
        if not self.profile_id.strip():
            raise ValueError("GarmentProfile.profile_id must be non-empty")

        copied = dict(self.measurements)

        unknown = set(copied) - GARMENT_MEASUREMENT_KEYS

        if unknown:
            raise ValueError(f"Unsupported garment measurement keys: {sorted(unknown)}")

        for name, measurement in copied.items():
            value = measurement.value_mm

            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be a finite positive measurement in mm")

        object.__setattr__(
            self,
            "measurements",
            types.MappingProxyType(copied),
        )

    def missing_or_unconfirmed(
        self,
        required: tuple[str, ...],
    ) -> tuple[str, ...]:
        """Return measurements that are missing or not confirmed."""

        missing: list[str] = []

        for name in required:
            measurement = self.measurements.get(name)

            if measurement is None or measurement.confirmed_at is None:
                missing.append(name)

        return tuple(missing)

    def get_confirmed_value_mm(self, name: str) -> float | None:
        """Return a confirmed measurement, or None if unavailable."""

        measurement = self.measurements.get(name)

        if measurement is None or measurement.confirmed_at is None:
            return None

        return measurement.value_mm
