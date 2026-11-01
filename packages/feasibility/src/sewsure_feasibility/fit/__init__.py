"""Fit and ease (N3): finished-garment dimensions, ease, fit labels and warnings (blueprint 7.1)."""

from sewsure_feasibility.fit.assess import SUPPORTED_RECIPE_IDS, assess_fit
from sewsure_feasibility.fit.config import EaseConfig, EaseProfile, load_config, parse_config
from sewsure_feasibility.fit.dimensions import FinishedDimensions, finished_dimensions
from sewsure_feasibility.fit.model import MAX_WARNING_CHARS, FitAssessment, FitLabel

__all__ = [
    "MAX_WARNING_CHARS",
    "SUPPORTED_RECIPE_IDS",
    "EaseConfig",
    "EaseProfile",
    "FinishedDimensions",
    "FitAssessment",
    "FitLabel",
    "assess_fit",
    "finished_dimensions",
    "load_config",
    "parse_config",
]
