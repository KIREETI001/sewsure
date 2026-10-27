import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import adapter  # noqa: E402


@pytest.fixture(scope="session")
def engine():
    """Skip (not fail) engine-backed tests while packages/feasibility is not importable."""
    try:
        adapter.load_engine()
    except adapter.EngineUnavailable as exc:
        pytest.skip(f"feasibility engine unavailable: {exc}")
    return adapter.evaluate_inputs
