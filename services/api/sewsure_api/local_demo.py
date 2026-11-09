"""Opt-in loopback demo entry point. Never imported by the production entry point.

Existing contract routes + isolated ephemeral DB, synthetic-owner sessions, local Proposer.
No .env, credentials, photo endpoints, Azure clients or production storage are loaded.
"""

import json
import re
from pathlib import Path
from typing import Any

from fastapi import Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic_settings import SettingsConfigDict
from sewsure_contracts.diy_steps_schema import DiySteps
from sqlalchemy.orm import Session

from sewsure_api import services
from sewsure_api.app import create_app, get_db
from sewsure_api.auth import CurrentUser, get_current_user
from sewsure_api.db import Base, make_engine, make_session_factory
from sewsure_api.generation import Proposer
from sewsure_api.local_model import LocalModelProposer
from sewsure_api.settings import Settings

ROOT = Path(__file__).resolve().parents[3]
ORIGINS = [f"http://{host}:8081" for host in ("localhost", "127.0.0.1")]


class DemoSettings(Settings):
    model_config = SettingsConfigDict(
        env_prefix="SEWSURE_DEMO_UNUSED_", env_file=None, extra="ignore"
    )


class DemoAuth:
    """Session separation only, deliberately not real authentication. No secret involved."""

    def authenticate(self, request: Request) -> CurrentUser | None:
        session = request.headers.get("X-SewSure-Demo", "")
        if re.fullmatch(r"[a-z0-9-]{16,48}", session):
            return CurrentUser(id=f"usr-{session}")
        return None


def demo_steps(revision_id: str, plan: dict[str, Any]) -> DiySteps:
    # Fixture review metadata is synthetic, never a sewist sign-off. This entry point only
    # serves labelled demo previews. Keep all numbers tied to the current engine cut plan.
    fixture = ROOT / "packages/contracts/fixtures/woven_shirt_crop_pass.json"
    doc = json.loads(fixture.read_text(encoding="utf-8"))["diy_steps"]
    doc["revision_id"] = revision_id
    doc["recipe_id"] = plan["recipe_id"]
    doc["recipe_version"] = plan["recipe_version"]
    checkpoint = plan["ruler_checkpoints"][0]
    mark = checkpoint["distance_mm"]
    tolerance = checkpoint["tolerance_mm"]
    for step in doc["steps"]:
        if step["phase"] == "mark":
            step["body"] = f"Demo: mark {mark / 10:g} cm down from the shoulder point."
        elif step["phase"] == "ruler_checkpoint":
            step["checkpoint_id"] = checkpoint["checkpoint_id"]
            step["body"] = (
                f"Demo: check {mark / 10:g} cm from shoulder to cut mark. "
                f"Provisional tolerance: {tolerance / 10:g} cm."
            )
        elif step["phase"] == "finish":
            step["body"] = (
                f"Demo hem allowance: {plan['allowances']['hem_allowance_mm'] / 10:g} cm. "
                "This draft recipe needs sewist review; do not use this demo to cut a garment."
            )
    return DiySteps.model_validate(doc)


def create_local_demo(proposer: Proposer | None = None):
    engine = make_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    app = create_app(
        settings=DemoSettings(database_url="sqlite:///:memory:"),
        session_factory=make_session_factory(engine),
        auth_provider=DemoAuth(),
        proposer=proposer or LocalModelProposer(),
    )
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver"]
    )

    @app.middleware("http")
    async def local_only(request: Request, call_next):
        origin = request.headers.get("origin")
        host = request.client.host if request.client else ""
        if host not in ("127.0.0.1", "::1", "testclient") or (origin and origin not in ORIGINS):
            return JSONResponse({"detail": "Loopback demo only"}, status_code=403)
        # Body profiles and photo content are never accepted by the demo service.
        if request.method in ("POST", "PUT", "PATCH"):
            data = await request.body()
            if len(data) > 16384:
                return JSONResponse({"detail": "Demo request too large"}, status_code=413)
            try:
                document = json.loads(data)
            except (ValueError, UnicodeDecodeError):
                return JSONResponse({"detail": "JSON required"}, status_code=422)
            inspiration = document.get("inspiration") if isinstance(document, dict) else None
            photos = inspiration.get("photo_ids") if isinstance(inspiration, dict) else None
            if isinstance(document, dict) and (
                document.get("body") or "photo" in request.url.path or photos
            ):
                return JSONResponse({"detail": "Synthetic garment data only"}, status_code=422)
        response = await call_next(request)
        response.headers["X-SewSure-Mode"] = "synthetic-local-demo"
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Content-Type", "Idempotency-Key", "X-SewSure-Demo"],
    )

    @app.get("/v1/revisions/{revision_id}/diy-steps", response_model=DiySteps)
    def read_demo_steps(
        revision_id: str,
        user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        # Same ownership, stale and non-passing guards as the matching cut plan.
        plan = services.get_cut_plan(db, user.id, revision_id)
        return demo_steps(revision_id, plan)

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(create_local_demo(), host="127.0.0.1", port=8090, access_log=False)
