"""Regenerate Pydantic models (services/api) and TypeScript types (apps/mobile) from the contract.

Usage (from packages/contracts):  python scripts/codegen.py [--python-only | --ts-only]
Needs the dev extras (pip install -e ".[dev]") and `npm install` for the TypeScript step.
Generated files are committed and never hand-edited. CI checks drift with:
    python scripts/codegen.py && git diff --exit-code generated/
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY_OUT = ROOT / "generated" / "python" / "sewsure_contracts"

DATAMODEL_ARGS = [
    "--input", "schemas",
    "--input-file-type", "jsonschema",
    "--output", str(PY_OUT.relative_to(ROOT)),
    "--output-model-type", "pydantic_v2.BaseModel",
    "--target-python-version", "3.12",
    "--use-standard-collections",
    "--use-union-operator",
    "--use-schema-description",
    "--use-field-description",
    "--field-constraints",
    "--use-title-as-name",
    "--disable-timestamp",
    "--collapse-root-models",
    "--use-annotated",
    "--set-default-enum-member",
    "--formatters", "black", "isort",
]


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True, shell=sys.platform == "win32" and cmd[0] == "npm")


def python_models() -> None:
    # The generator writes one module per schema; clear old modules so removed schemas disappear.
    shutil.rmtree(PY_OUT, ignore_errors=True)
    run([sys.executable, "-m", "datamodel_code_generator", *DATAMODEL_ARGS])


def ts_types() -> None:
    run(["npm", "run", "--silent", "gen:ts"])


def main() -> None:
    args = set(sys.argv[1:])
    if "--ts-only" not in args:
        python_models()
    if "--python-only" not in args:
        ts_types()


if __name__ == "__main__":
    main()
