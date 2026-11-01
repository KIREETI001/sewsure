"""Regression tests for X1's review of PR #22 (findings 1-8). Each drives the HTTP API."""

from typing import Any

from fastapi.testclient import TestClient

from tests.conftest import ALICE, CONFIRMED, idem


def val(mm: float, *, confirmed: bool = True, origin: str = "user_tape_measured") -> dict[str, Any]:
    return {"value_mm": mm, "origin": origin, "confirmed_at": CONFIRMED if confirmed else None}


def dims(length: float = 780, placket: float | None = 700, **extra: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"shoulder_to_hem": val(length), "chest_flat_width": val(560)}
    if placket is not None:
        out["placket_end_from_shoulder"] = val(placket)
    out.update(extra)
    return out


def project(client: TestClient, key: str = "proj") -> str:
    r = client.post(
        "/v1/projects",
        json={"garment": {"category": "woven_shirt", "fabric_family": "woven"}},
        headers={**ALICE, **idem(key)},
    )
    return r.json()["project_id"]


def put(client: TestClient, pid: str, d: dict[str, Any]) -> dict[str, Any]:
    r = client.put(
        f"/v1/projects/{pid}/measurements", json={"units": "mm", "garment": d}, headers=ALICE
    )
    assert r.status_code == 200, r.text
    return r.json()


def generate(
    client: TestClient, pid: str, transformation: str, target: float, key: str = "gen"
) -> None:
    body = {
        "inspiration": {
            "text": "x",
            "skill_level": "beginner",
            "tools": ["ruler"],
            "requested_features": {
                "transformation": transformation,
                "target_finished_length_mm": target,
            },
        }
    }
    r = client.post(f"/v1/projects/{pid}/generate", json=body, headers={**ALICE, **idem(key)})
    assert r.status_code == 202, r.text


def designs(client: TestClient, pid: str) -> dict[str, Any]:
    return client.get(f"/v1/projects/{pid}/designs", headers=ALICE).json()


def first(client: TestClient, pid: str) -> dict[str, Any]:
    d = designs(client, pid)["designs"][0]
    return client.get(f"/v1/revisions/{d['current_revision_id']}", headers=ALICE).json()


def edit(client: TestClient, rev: dict[str, Any], key: str, **params: Any):
    return client.post(
        f"/v1/designs/{rev['design_id']}/revisions",
        json={"parent_revision_id": rev["revision_id"], "parameters": params},
        headers={**ALICE, **idem(key)},
    )


def cut_plan(client: TestClient, revision_id: str):
    return client.get(f"/v1/revisions/{revision_id}/cut-plan", headers=ALICE)


def test_superseded_revision_returns_no_cut_plan(client: TestClient) -> None:  # finding 1
    pid = project(client)
    put(client, pid, dims())
    generate(client, pid, "crop", 500)
    old = first(client, pid)
    assert cut_plan(client, old["revision_id"]).status_code == 200
    assert edit(client, old, "e1", finished_length_mm=450).status_code == 201
    r = cut_plan(client, old["revision_id"])
    assert r.status_code == 409
    assert r.json()["code"] == "REVISION_NOT_PASSING"


def test_unconfirmed_placket_does_not_supply_the_zone(client: TestClient) -> None:  # finding 2
    pid = project(client)
    result = put(
        client,
        pid,
        dims(
            placket=None,
            placket_end_from_shoulder=val(600, confirmed=False, origin="vision_suggested"),
        ),
    )
    assert "placket_end_from_shoulder" in result["missing_dimensions"]
    generate(client, pid, "crop", 500)
    d = designs(client, pid)["designs"][0]
    assert d["status"] == "NEEDS_INPUT"
    assert "placket_end_from_shoulder" in d["missing_dimensions"]
    assert "prohibited_regions" not in d["missing_dimensions"]
    rev = first(client, pid)
    assert rev["cut_plan_id"] is None
    assert cut_plan(client, rev["revision_id"]).status_code == 409


def test_missing_placket_is_reported_as_a_measurement(client: TestClient) -> None:  # finding 7
    pid = project(client)
    result = put(client, pid, dims(placket=None))
    assert "placket_end_from_shoulder" in result["missing_dimensions"]
    assert any(i["dimension"] == "placket_end_from_shoulder" for i in result["issues"])


def test_corrected_measurements_take_effect(client: TestClient) -> None:  # finding 3
    pid = project(client)
    put(client, pid, dims(length=780, placket=700))
    generate(client, pid, "crop", 600)
    old = first(client, pid)
    assert old["status"] == "PASS_SUPPORTED_CHECKS"
    put(client, pid, dims(length=500, placket=450))  # the user re-measures
    # The earlier pass no longer hands out a cut plan and says it needs a recheck.
    stale = cut_plan(client, old["revision_id"])
    assert stale.status_code == 409
    assert stale.json()["code"] == "REVISION_STALE"
    assert any("recheck" in c.lower() for c in _rev(client, old)["pending_checks"])
    # An edit evaluates against the current measurements, not the replaced ones.
    new = edit(client, old, "e2", finished_length_mm=620).json()
    assert new["geometry_mm"].get("original_length_mm") == 500
    assert new["status"] == "FAILED_CHECKS"
    assert new["cut_plan_id"] is None


def test_confirming_a_measurement_unblocks_an_edit(client: TestClient) -> None:  # finding 3
    pid = project(client)
    put(client, pid, dims(length=780, placket=700) | {"shoulder_to_hem": val(780, confirmed=False)})
    generate(client, pid, "crop", 500)
    parent = first(client, pid)
    assert parent["status"] == "NEEDS_INPUT"
    put(client, pid, dims(length=780, placket=700))  # now confirmed
    new = edit(client, parent, "e3", finished_length_mm=500).json()
    assert new["status"] == "PASS_SUPPORTED_CHECKS"


def _rev(client: TestClient, rev: dict[str, Any]) -> dict[str, Any]:
    return client.get(f"/v1/revisions/{rev['revision_id']}", headers=ALICE).json()


def test_regenerate_shows_only_the_latest_job(client: TestClient) -> None:  # finding 4
    pid = project(client)
    put(client, pid, dims())
    generate(client, pid, "crop", 500, "g1")
    assert designs(client, pid)["designs"][0]["status"] == "PASS_SUPPORTED_CHECKS"
    generate(client, pid, "lengthen", 900, "g2")
    listing = designs(client, pid)
    assert [d["status"] for d in listing["designs"]] == ["FAILED_CHECKS"]
    assert listing["binding_constraint"]["hard_pass"] is False


def test_placket_gate_is_not_trivially_satisfiable(client: TestClient) -> None:  # finding 5
    for i, placket in enumerate([779, 780, 800]):
        pid = project(client, f"pk{i}")
        put(client, pid, dims(length=780, placket=placket))
        generate(client, pid, "crop", 500)
        assert designs(client, pid)["designs"][0]["status"] == "NEEDS_INPUT", placket
    # A cut 1 mm above the placket zone is refused: clearance must exceed the ruler tolerance.
    pid = project(client, "pk-near")
    put(client, pid, dims(length=780, placket=531))
    generate(client, pid, "crop", 500)  # cut mark 530
    d = designs(client, pid)["designs"][0]
    assert d["status"] != "PASS_SUPPORTED_CHECKS"
    assert first(client, pid)["cut_plan_id"] is None


def test_lengthen_request_never_returns_a_shortening_plan(client: TestClient) -> None:  # finding 6
    pid = project(client)
    put(client, pid, dims())
    generate(client, pid, "lengthen", 500)  # shorter than the 780 mm garment
    d = designs(client, pid)["designs"][0]
    assert d["status"] != "PASS_SUPPORTED_CHECKS"
    assert first(client, pid)["cut_plan_id"] is None


def test_cut_plan_lists_the_prohibited_region(client: TestClient) -> None:  # finding 8
    pid = project(client)
    put(client, pid, dims())
    generate(client, pid, "crop", 500)
    plan = cut_plan(client, first(client, pid)["revision_id"]).json()
    fronts = [p for p in plan["pieces"] if p["source_panel"].startswith("front")]
    assert fronts
    assert all(p["prohibited_regions"] == ["placket_end"] for p in fronts)
