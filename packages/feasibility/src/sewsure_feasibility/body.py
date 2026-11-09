"""Body profile models for body-aware garment fit evaluation.

All measurements are stored in millimetres.
The existing Measurement class is reused.
"""

from __future__ import annotations

import math
import types
from collections.abc import Mapping
from dataclasses import dataclass

import sewsure_feasibility.models

# Accepted body measurements for SewSure's first iteration.
BODY_MEASUREMENT_KEYS = frozenset(
    {
        "bust_circumference",
        "waist_circumference",
        "hip_circumference",
        "shoulder_breadth",
        "torso_length",
        "upper_arm_circumference",
        "armhole_depth",
    }
)


@dataclass(frozen=True)
class BodyProfile:
    """Stores a user's manually measured body dimensions."""

    profile_id: str
    measurements: Mapping[str, sewsure_feasibility.models.Measurement]

    def __post_init__(self) -> None:
        if not self.profile_id.strip():
            raise ValueError("BodyProfile.profile_id must be non-empty")

        # Copy the measurements to prevent external modification.
        copied = dict(self.measurements)

        # Reject measurements that SewSure does not currently support.
        unknown = set(copied) - BODY_MEASUREMENT_KEYS

        if unknown:
            raise ValueError(f"Unsupported body measurement keys: {sorted(unknown)}")

        # Every supplied measurement must be finite and positive.
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
