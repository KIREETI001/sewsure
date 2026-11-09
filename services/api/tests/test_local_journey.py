"""Synthetic HTTP journey with fake model; a separate smoke command exercises real inference."""

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sewsure_contracts.diy_steps_schema import DiySteps

from sewsure_api.local_demo import create_local_demo
from sewsure_api.local_model import LocalModelProposer

ALICE = {"X-SewSure-Demo": "demo-alice-000000001"}
BOB = {"X-SewSure-Demo": "demo-bob-00000000001"}
CROP = (
    '{"proposals":[{"recipe_id":"woven_shirt_crop_v1","parameters":{"hem_finish":"double_fold"}}]}'
)


class FakeLocalModel(LocalModelProposer):
    def __init__(self, output: str = CROP):
        self.output = output
        self.calls: list[str] = []

    def complete(self, text: str) -> str:
        self.calls.append(text)
        return self.output


def start(client: TestClient, *, placket: bool = True, transformation: str = "crop"):
    headers = {**ALICE, "Idempotency-Key": "local-journey-0001"}
    project = client.post(
        "/v1/projects",
        json={
            "garment": {"category": "woven_shirt", "fabric_family": "woven"},
        },
        headers=headers,
    ).json()["project_id"]
    dims = {
        "shoulder_to_hem": 700,
        "chest_flat_width": 520,
        "shoulder_width": 450,
        "sleeve_length": 600,
    }
    if placket:
        dims["placket_end_from_shoulder"] = 600
    garment = {
        k: {"value_mm": v, "origin": "user_entered", "confirmed_at": "2026-11-09T10:00:00Z"}
        for k, v in dims.items()
    }
    assert (
        client.put(
            f"/v1/projects/{project}/measurements",
            json={
                "units": "mm",
                "garment": garment,
            },
            headers=ALICE,
        ).status_code
        == 200
    )
    job = client.post(
        f"/v1/projects/{project}/generate",
        json={
            "inspiration": {
                "text": "Crop the bottom of the synthetic woven shirt.",
                "requested_features": {
                    "transformation": transformation,
                    "target_finished_length_mm": 450,
                },
                "skill_level": "beginner",
                "tools": [],
            }
        },
        headers=headers,
    )
    assert job.status_code == 202
    finished = client.get(f"/v1/jobs/{job.json()['job_id']}", headers=ALICE).json()
    designs = client.get(f"/v1/projects/{project}/designs", headers=ALICE).json()
    return project, finished, designs


def test_edit_closes_old_guide_and_opens_new_guide_with_matching_steps():
    model = FakeLocalModel()
    with TestClient(create_local_demo(model)) as client:
        project, job, designs = start(client)
        assert job["state"] == "complete"
        design = designs["designs"][0]
        old = design["current_revision_id"]
        assert design["status"] == "PASS_SUPPORTED_CHECKS"
        first_plan = client.get(f"/v1/revisions/{old}/cut-plan", headers=ALICE).json()
        assert first_plan["ruler_checkpoints"][0]["distance_mm"] == 480
        edit = client.post(
            f"/v1/designs/{design['design_id']}/revisions",
            headers={
                **ALICE,
                "Idempotency-Key": "local-edit-0000001",
            },
            json={"parent_revision_id": old, "parameters": {"finished_length_mm": 470}},
        )
        assert edit.status_code == 201, edit.text
        new = edit.json()["revision_id"]
        assert new != old
        assert client.get(f"/v1/revisions/{old}/cut-plan", headers=ALICE).status_code == 409
        assert client.get(f"/v1/revisions/{old}/diy-steps", headers=ALICE).status_code == 409
        plan = client.get(f"/v1/revisions/{new}/cut-plan", headers=ALICE).json()
        steps = client.get(f"/v1/revisions/{new}/diy-steps", headers=ALICE)
        assert steps.status_code == 200
        doc = DiySteps.model_validate(steps.json())
        assert doc.revision_id == new
        assert doc.recipe_version == plan["recipe_version"]
        assert plan["ruler_checkpoints"][0]["distance_mm"] == 500
        checkpoint = next(s for s in doc.steps if s.phase == "ruler_checkpoint")
        assert checkpoint.checkpoint_id is not None
        assert checkpoint.checkpoint_id.root == plan["ruler_checkpoints"][0]["checkpoint_id"]
        assert "50 cm" in checkpoint.body
        assert "525" not in steps.text  # Never reuse the fixture's old cut mark.
        assert client.get(f"/v1/revisions/{new}/diy-steps", headers=BOB).status_code == 404
        assert client.get(f"/v1/projects/{project}", headers=BOB).status_code == 404
        assert model.calls == ["Crop the bottom of the synthetic woven shirt."]


@pytest.mark.parametrize(
    "placket,transformation,expected",
    [
        (False, "crop", "NEEDS_INPUT"),
        (True, "lengthen", "IDEA_ONLY"),
        (True, "other", "IDEA_ONLY"),
    ],
)
def test_no_guide_for_missing_or_unsupported_inputs(placket, transformation, expected):
    with TestClient(create_local_demo(FakeLocalModel())) as client:
        _, job, designs = start(client, placket=placket, transformation=transformation)
        assert job["state"] == "complete"
        design = designs["designs"][0]
        assert design["status"] == expected
        assert (
            client.get(
                f"/v1/revisions/{design['current_revision_id']}/cut-plan", headers=ALICE
            ).status_code
            == 409
        )


@pytest.mark.parametrize(
    "output",
    [
        "not json",
        '{"proposals":[{"recipe_id":"unknown_v1","parameters":{}}]}',
        '{"proposals":[{"recipe_id":"woven_shirt_crop_v1","parameters":{"finished_length_mm":450}}]}',
        '{"proposals":[],"status":"PASS_SUPPORTED_CHECKS"}',
    ],
)
def test_bad_model_output_fails_job_without_creating_a_design(output):
    with TestClient(create_local_demo(FakeLocalModel(output))) as client:
        _, job, designs = start(client)
        assert job["state"] == "failed"
        assert job["error"]["recoverable"] is True
        assert designs["designs"] == []


def test_no_auth_cross_origin_body_or_photo_access():
    with TestClient(create_local_demo(FakeLocalModel())) as client:
        assert (
            client.post(
                "/v1/projects/prj-demo/generate", headers=ALICE, json={"inspiration": None}
            ).status_code
            == 422
        )
        assert client.get("/v1/projects/prj-missing").status_code == 401
        assert client.get("/healthz", headers={"Origin": "https://example.com"}).status_code == 403
        assert (
            client.post("/v1/projects", headers=ALICE, json={"body": {"bust": 900}}).status_code
            == 422
        )
        assert (
            client.post(
                "/v1/projects/prj-demo/generate",
                headers=ALICE,
                json={"inspiration": {"photo_ids": ["photo-demo"]}},
            ).status_code
            == 422
        )


def test_unavailable_model_fails_without_mock_fallback():
    class Unavailable(FakeLocalModel):
        def complete(self, text: str) -> str:
            raise TimeoutError("local model unavailable")

    with TestClient(create_local_demo(Unavailable())) as client:
        _, job, designs = start(client)
        assert job["state"] == "failed"
        assert designs["designs"] == []


def test_prompt_contains_only_request_not_measurements(monkeypatch):
    from sewsure_api import local_model

    captured: list[dict[str, Any]] = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def geturl(self):
            return local_model.MODEL_URL

        def read(self, limit):
            return json.dumps({"choices": [{"message": {"content": CROP}}]}).encode()

    class Opener:
        def open(self, request, timeout):
            captured.append(json.loads(request.data))
            assert request.full_url == local_model.MODEL_URL
            return Response()

    monkeypatch.setattr(local_model, "build_opener", lambda *args: Opener())
    model = LocalModelProposer()
    assert model.complete("synthetic crop") == CROP
    user_message = captured[0]["messages"][1]["content"]
    assert json.loads(user_message) == {"synthetic_request": "synthetic crop"}
