"""Build fixtures/*.json, the mock scenarios mobile and tests run against.

Usage (from packages/contracts):  python scripts/build_fixtures.py
All values are synthetic and illustrative (blueprint §5.3), not measured evidence.
Edit this script, not the JSON, then run scripts/validate.py.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures"

SCHEMA_VERSION = "1.0"
ENGINE_VERSION = "0.1.0"
T0 = "2026-10-28T09:00:00Z"
T1 = "2026-10-28T09:01:30Z"
T2 = "2026-10-28T09:05:00Z"
PROVENANCE = {"source": "mock", "schema_version": SCHEMA_VERSION, "engine_version": ENGINE_VERSION, "model_id": None, "prompt_version": None}
CROP = "woven_shirt_crop_v1"


def inputs_hash(inputs: dict[str, Any], recipe_id: str | None, recipe_version: str | None, parameters: dict[str, Any]) -> str:
    """SHA-256 of canonical JSON (sorted keys, no whitespace) of the check inputs. Same rule the API must use."""
    payload = {"inputs": inputs, "recipe_id": recipe_id, "recipe_version": recipe_version, "parameters": parameters}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def mv(value_mm: float, origin: str = "user_tape_measured", confirmed: str | None = T0, entered_unit: str = "cm") -> dict[str, Any]:
    return {"value_mm": value_mm, "origin": origin, "confirmed_at": confirmed, "entered_unit": entered_unit, "note": None}


def user() -> dict[str, Any]:
    return {
        "user_id": "usr-demo-01",
        "role": "user",
        "display_name": "Demo user",
        "profile_ref": None,
        "consent": {"consent_version": "2026-10-draft", "accepted_at": T0, "body_measurements": False, "image_use": "app_only", "withdrawn_at": None},
        "created_at": T0,
    }


def project(key: str, measurements_id: str | None, job_id: str) -> dict[str, Any]:
    return {
        "project_id": f"prj-{key}",
        "owner_id": "usr-demo-01",
        "garment_id": f"gar-{key}",
        "title": None,
        "measurements_id": measurements_id,
        "latest_job_id": job_id,
        "created_at": T0,
        "updated_at": T1,
    }


def photo(key: str, view: str) -> dict[str, Any]:
    return {
        "photo_id": f"pho-{key}-{view}",
        "garment_id": f"gar-{key}",
        "view": view,
        "storage_ref": f"mock/garments/gar-{key}/{view}.jpg",
        "content_type": "image/jpeg",
        "byte_size": 1843200,
        "width_px": 3024,
        "height_px": 4032,
        "status": "verified",
        "has_calibration_marker": True,
        "image_use_consent": "app_only",
        "created_at": T0,
    }


def garment(key: str, category: str, fabric: str, features: list[str]) -> dict[str, Any]:
    return {
        "garment_id": f"gar-{key}",
        "project_id": f"prj-{key}",
        "owner_id": "usr-demo-01",
        "category": category,
        "fabric_family": fabric,
        "attribute_origin": "ai_suggested_user_confirmed",
        "attributes_confirmed_at": T0,
        "visible_features": features,
        "condition_notes": None,
        "photos": [photo(key, "front"), photo(key, "back")],
        "created_at": T0,
        "updated_at": T0,
    }


def measurements(key: str, garment_dims: dict[str, Any], issues: list[dict[str, Any]], missing: list[str]) -> dict[str, Any]:
    return {
        "measurements": {
            "measurements_id": f"msr-{key}",
            "project_id": f"prj-{key}",
            "units": "mm",
            "garment": garment_dims,
            "body": None,
            "updated_at": T0,
        },
        "issues": issues,
        "missing_dimensions": missing,
    }


def inspiration(key: str, text: str, features: dict[str, Any]) -> dict[str, Any]:
    return {
        "inspiration_id": f"ins-{key}",
        "project_id": f"prj-{key}",
        "text": text,
        "photo_ids": [],
        "requested_features": features,
        "surprise_me": False,
        "skill_level": "beginner",
        "tools": ["ruler", "chalk", "fabric_scissors", "hand_needle", "iron"],
        "supplies": [],
        "recogniser_notes": None,
        "created_at": T0,
    }


def job(key: str, state: str, design_ids: list[str] | None, outcome: str | None = None, error: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "job_id": f"job-{key}",
        "kind": "generate_designs",
        "project_id": f"prj-{key}",
        "state": state,
        "stage": None,
        "result": None if design_ids is None else {"outcome": outcome, "design_ids": design_ids},
        "error": error,
        "created_at": T0,
        "updated_at": T1,
    }


def checks(
    hard_pass: bool,
    outcomes: list[tuple[str, str, str | None]],
    residuals: list[dict[str, Any]] | None = None,
    missing: list[str] | None = None,
    flags: list[str] | None = None,
    alternatives: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    failure_codes = sorted({code for _, result, code in outcomes if code and result in {"fail", "needs_input"}})
    return {
        "hard_pass": hard_pass,
        "failure_codes": failure_codes,
        "residuals": residuals or [],
        "missing_dimensions": missing or [],
        "uncertainty_flags": flags or [],
        "checks": [{"check_id": cid, "result": result, "failure_code": code, "detail": None} for cid, result, code in outcomes],
        "alternatives": alternatives or [],
        "engine_version": ENGINE_VERSION,
        "checked_at": T1,
    }


def revision(
    key: str,
    design: str,
    n: int,
    *,
    category: str,
    fabric: str,
    recipe_id: str | None,
    parameters: dict[str, Any],
    geometry: dict[str, float],
    check: dict[str, Any],
    status: str,
    diy: str | None,
    pending: list[str],
    measurements_id: str | None,
    parent: str | None = None,
    cut_plan_id: str | None = None,
    superseded_by: str | None = None,
    preview_kind: str = "silhouette_2d",
) -> dict[str, Any]:
    recipe_version = "1.0" if recipe_id else None
    inputs = {
        "measurements_id": measurements_id,
        "garment_category": category,
        "fabric_family": fabric,
        "inspiration_id": f"ins-{key}",
        "calibration_id": None,
    }
    rev_id = f"rev-{design}-{n}"
    return {
        "revision_id": rev_id,
        "design_id": f"des-{design}",
        "project_id": f"prj-{key}",
        "garment_id": f"gar-{key}",
        "parent_revision_id": parent,
        "revision_number": n,
        "inputs_hash": inputs_hash(inputs, recipe_id, recipe_version, parameters),
        "inputs": inputs,
        "recipe_id": recipe_id,
        "recipe_version": recipe_version,
        "parameters": parameters,
        "units": "mm",
        "geometry_mm": geometry,
        "checks": check,
        "status": status,
        "diy_suitability": diy,
        "pending_checks": pending,
        "fit": None,
        "cut_plan_id": cut_plan_id,
        "preview": {"preview_id": f"prv-{design}-{n}", "approximate": True, "kind": preview_kind, "photo_id": None},
        "superseded_by_revision_id": superseded_by,
        "provenance": PROVENANCE,
        "created_at": T1,
    }


def candidate(rev: dict[str, Any], rank: int, title: str, explanation: str, panels: list[str]) -> dict[str, Any]:
    return {
        "design_id": rev["design_id"],
        "project_id": rev["project_id"],
        "rank": rank,
        "title": title,
        "current_revision_id": rev["revision_id"],
        "status": rev["status"],
        "recipe_id": rev["recipe_id"],
        "parameters": rev["parameters"],
        "required_panels": panels,
        "explanation": explanation,
        "failure_codes": rev["checks"]["failure_codes"],
        "missing_dimensions": rev["checks"]["missing_dimensions"],
        "preview": rev["preview"],
        "provenance": PROVENANCE,
        "created_at": T1,
    }


def crop_geometry(shoulder_to_hem: float, finished: float, hem: float) -> dict[str, float]:
    cut_mark = finished + hem
    return {
        "original_length_mm": shoulder_to_hem,
        "finished_length_mm": finished,
        "hem_allowance_mm": hem,
        "cut_mark_from_shoulder_mm": cut_mark,
        "fabric_removed_mm": shoulder_to_hem - cut_mark,
    }


def length_residual(required: float, available: float) -> dict[str, Any]:
    return {
        "check_id": "length_gate",
        "quantity": "garment_length",
        "required_mm": required,
        "available_mm": available,
        "residual_mm": available - required,
        "tolerance_mm": 0,
    }


PASS_OUTCOMES: list[tuple[str, str, str | None]] = [
    ("supported_material", "pass", None),
    ("required_dimensions", "pass", None),
    ("length_gate", "pass", None),
    ("structure", "pass", None),
    ("construction", "pass", None),
]
SHIRT_DIMS = {"shoulder_to_hem": mv(780), "chest_flat_width": mv(560), "hem_width": mv(540)}
CROP_EXPLANATION = "Crop to {f} mm finished length with a {h} mm hem turn-up. The cut mark sits {c} mm below the shoulder point. Side seams are not verified by this check; measure with a ruler before cutting."


def woven_shirt_crop_pass() -> dict[str, Any]:
    key = "crop"
    # Design A: first revision passed, the user then changed the hem allowance (rev 2). Rev 1 is SUPERSEDED.
    a1_params = {"finished_length_mm": 500, "hem_allowance_mm": 30, "hem_finish": "double_fold"}
    a2_params = {**a1_params, "hem_allowance_mm": 25}
    common = dict(category="woven_shirt", fabric="woven", recipe_id=CROP, diy="DIY_WITH_PRACTICE", measurements_id=f"msr-{key}")
    pending = ["Verify the shoulder-to-hem reference with a ruler on the garment before cutting."]
    a1 = revision(
        key, "crop-a", 1, parameters=a1_params, geometry=crop_geometry(780, 500, 30),
        check=checks(True, PASS_OUTCOMES, [length_residual(530, 780)], flags=["SIDE_SEAMS_NOT_VERIFIED"]),
        status="SUPERSEDED", pending=pending, cut_plan_id="cut-crop-a-1", superseded_by="rev-crop-a-2", **common,
    )
    a2 = revision(
        key, "crop-a", 2, parameters=a2_params, geometry=crop_geometry(780, 500, 25),
        check=checks(True, PASS_OUTCOMES, [length_residual(525, 780)], flags=["SIDE_SEAMS_NOT_VERIFIED"]),
        status="PASS_SUPPORTED_CHECKS", pending=pending, cut_plan_id="cut-crop-a-2", parent="rev-crop-a-1", **common,
    )
    b_params = {"finished_length_mm": 450, "hem_allowance_mm": 30, "hem_finish": "double_fold"}
    b1 = revision(
        key, "crop-b", 1, parameters=b_params, geometry=crop_geometry(780, 450, 30),
        check=checks(True, PASS_OUTCOMES, [length_residual(480, 780)], flags=["SIDE_SEAMS_NOT_VERIFIED"]),
        status="PASS_SUPPORTED_CHECKS", pending=pending, cut_plan_id="cut-crop-b-1", **common,
    )
    panels = ["back_panel", "front_left", "front_right"]
    designs = [
        candidate(a2, 1, "Cropped shirt, 500 mm", CROP_EXPLANATION.format(f=500, h=25, c=525), panels),
        candidate(b1, 2, "Short crop, 450 mm", CROP_EXPLANATION.format(f=450, h=30, c=480), panels),
    ]
    cut_plan = {
        "cut_plan_id": "cut-crop-a-2",
        "revision_id": "rev-crop-a-2",
        "recipe_id": CROP,
        "recipe_version": "1.0",
        "units": "mm",
        "mode": "dimensioned_diagram",
        "coordinate_frame": {
            "origin_landmark": "high_shoulder_point",
            "x_axis": "across the body, towards centre front",
            "y_axis": "downwards, towards the hem",
        },
        "pieces": [
            {
                "piece_id": side,
                "source_panel": side,
                "lines": [
                    {"line_id": "cut_line", "kind": "cut", "points_mm": [[0, 525], [280, 525]], "label": "Cut 525 mm below shoulder"},
                    {"line_id": "fold_line", "kind": "fold", "points_mm": [[0, 512.5], [280, 512.5]], "label": "First fold"},
                    {"line_id": "hem_line", "kind": "fold", "points_mm": [[0, 500], [280, 500]], "label": "Finished hem 500 mm"},
                ],
                "prohibited_regions": ["button_placket"] if side != "back_panel" else [],
            }
            for side in ["front_left", "front_right", "back_panel"]
        ],
        "allowances": {"seam_allowance_mm": 0, "hem_allowance_mm": 25},
        "ruler_checkpoints": [
            {
                "checkpoint_id": "cut_mark_front",
                "instruction": "Measure straight down from the high shoulder point and mark the cut line with chalk.",
                "from_landmark": "high_shoulder_point",
                "distance_mm": 525,
                "tolerance_mm": 3,
            },
            {
                "checkpoint_id": "cut_mark_back",
                "instruction": "Repeat on the back from the shoulder seam and check both marks line up at the side seams.",
                "from_landmark": "shoulder_seam",
                "distance_mm": 525,
                "tolerance_mm": 3,
            },
        ],
        "calibration": {
            "state": "uncalibrated",
            "calibration_id": None,
            "reference_photo_id": "pho-crop-front",
            "scale_px_per_mm": None,
            "median_error_mm": None,
            "max_error_mm": None,
            "tolerance_mm": None,
            "rejection_reason": "No calibration has been run for this mock.",
        },
        "provenance": PROVENANCE,
        "created_at": T2,
    }
    steps = [
        ("prepare", "Press the shirt", "Lay the shirt flat on a hard surface and smooth out folds.", False, None),
        ("measure", "Find the shoulder point", "Locate the high shoulder point on each front panel.", False, None),
        ("mark", "Mark the cut line", "Mark 525 mm down from the shoulder point with chalk.", False, None),
        ("ruler_checkpoint", "Check the marks", "Re-measure both marks with a ruler. They must read 525 mm, within 3 mm.", False, "cut_mark_front"),
        ("cut", "Cut along the line", "Cut through one layer at a time along the chalk line.", True, None),
        ("finish", "Hem", "Fold 12.5 mm, press, fold again and stitch close to the inner fold.", False, None),
        ("verify", "Measure the result", "Measure the finished length from the shoulder point and record it.", False, None),
    ]
    diy_steps = {
        "revision_id": "rev-crop-a-2",
        "recipe_id": CROP,
        "recipe_version": "1.0",
        "review": {"reviewed_on": "2026-10-20", "reviewer_role": "supervisor"},
        "required_tools": ["ruler", "chalk", "fabric_scissors", "hand_needle", "iron"],
        "skill_prerequisites": ["straight_hand_stitch", "double_fold_hem"],
        "materials": ["Original shirt", "Matching thread"],
        "steps": [
            {"step_id": f"s{i}_{phase}", "order": i, "phase": phase, "title": title, "body": body, "irreversible": irr, "checkpoint_id": cp, "media_refs": []}
            for i, (phase, title, body, irr, cp) in enumerate(steps, start=1)
        ],
        "practice_exercises": [
            {"step_id": "p1_hem_scrap", "order": 1, "phase": "practice", "title": "Practise a hem", "body": "Hem a 200 mm scrap strip before working on the shirt.", "irreversible": False, "checkpoint_id": None, "media_refs": []}
        ],
        "extra_tools_or_skills_required": False,
    }
    diy_progress = {
        "progress_id": "prg-crop-a-2",
        "revision_id": "rev-crop-a-2",
        "user_id": "usr-demo-01",
        "steps": [
            {"step_id": "s1_prepare", "self_verification": "self_reported_done", "checked_at": T2, "measured_mm": None},
            {"step_id": "s2_measure", "self_verification": "self_reported_done", "checked_at": T2, "measured_mm": None},
            {"step_id": "s3_mark", "self_verification": "not_started", "checked_at": None, "measured_mm": None},
        ],
        "updated_at": T2,
    }
    maker_request = {
        "request_id": "req-crop-a-2",
        "user_id": "usr-demo-01",
        "tailor_id": "usr-tailor-01",
        "revision_id": "rev-crop-a-2",
        "brief": {
            "verification_label": "verified_checks",
            "design_status": "PASS_SUPPORTED_CHECKS",
            "garment_category": "woven_shirt",
            "modification_request": "Crop to 500 mm finished length with a double-fold hem.",
            "shared_photo_ids": ["pho-crop-front"],
            "shared_measurements": {"shoulder_to_hem": 780},
            "unresolved_checks": pending,
            "consent": {"consent_version": "2026-10-draft", "shared_fields": ["garment_category", "photos.front", "measurements.shoulder_to_hem"], "consented_at": T2},
        },
        "status": "QUOTED",
        "price_estimate": {"amount_minor": 1500, "currency": "SGD"},
        "created_at": T2,
        "updated_at": T2,
    }
    quotes = [
        {
            "quote_id": "quo-crop-a-2",
            "request_id": "req-crop-a-2",
            "tailor_id": "usr-tailor-01",
            "kind": "quote",
            "price": {"amount_minor": 1500, "currency": "SGD"},
            "estimated_duration_days": 3,
            "message": "Mock quote for UI work.",
            "created_at": T2,
        }
    ]
    evidence = [
        {
            "evidence_id": "evd-crop-001",
            "kind": "constraint_benchmark",
            "input_case_id": "C01_normal_crop",
            "revision_id": "rev-crop-a-2",
            "outcome": "correct_accept",
            "predicted_mm": {"cut_mark_from_shoulder": 525},
            "actual_mm": {},
            "abs_error_mm": {},
            "corrections": [],
            "notes": "Mock record showing the shape only. Not a measured result.",
            "duration_min": None,
            "cost": None,
            "anonymous": True,
            "media_consent": "none",
            "recorded_at": T2,
        }
    ]
    return {
        "mock": True,
        "scenario": "woven_shirt_crop_pass",
        "description": "Feasible crop of a woven shirt. Two designs (not three); design A was edited once, so rev 1 is SUPERSEDED and rev 2 passed. Includes cut plan, DIY steps, progress and a tailor quote.",
        "user": user(),
        "project": project(key, f"msr-{key}", f"job-{key}"),
        "garment": garment(key, "woven_shirt", "woven", ["button_placket", "chest_pocket", "curved_hem"]),
        "measurements": measurements(key, SHIRT_DIMS, [], []),
        "inspiration": inspiration(key, "Make it a cropped shirt I can wear over a dress.", {"transformation": "crop", "target_finished_length_mm": 500, "closure_preservation": True}),
        "job": job(key, "complete", ["des-crop-a", "des-crop-b"], "designs"),
        "designs": {"project_id": f"prj-{key}", "job_id": f"job-{key}", "designs": designs, "binding_constraint": None},
        "revisions": [a1, a2, b1],
        "cut_plan": cut_plan,
        "diy_steps": diy_steps,
        "diy_progress": diy_progress,
        "maker_request": maker_request,
        "quotes": quotes,
        "evidence": evidence,
    }


def lengthening_impossible() -> dict[str, Any]:
    key = "longer"
    params = {"finished_length_mm": 900, "hem_allowance_mm": 30, "hem_finish": "double_fold"}
    alternative = {
        "recipe_id": CROP,
        "parameters": {"finished_length_mm": 600, "hem_allowance_mm": 30, "hem_finish": "double_fold"},
        "reason": "The shirt has 780 mm of length. A 600 mm crop fits within it.",
    }
    check = checks(
        False,
        [
            ("supported_material", "pass", None),
            ("required_dimensions", "pass", None),
            ("length_gate", "fail", "INSUFFICIENT_LENGTH"),
            ("structure", "not_run", None),
            ("construction", "not_run", None),
        ],
        [length_residual(930, 780)],
        alternatives=[alternative],
    )
    rev = revision(
        key, "longer-a", 1, category="woven_shirt", fabric="woven", recipe_id=CROP, parameters=params,
        geometry={"original_length_mm": 780, "finished_length_mm": 900, "hem_allowance_mm": 30, "required_length_mm": 930},
        check=check, status="FAILED_CHECKS", diy=None, pending=[], measurements_id=f"msr-{key}",
    )
    explanation = "A 900 mm finished length needs 930 mm of fabric including the hem, but the shirt is 780 mm long (150 mm short). Adding length needs extra fabric, which no reviewed recipe supports yet."
    return {
        "mock": True,
        "scenario": "lengthening_impossible",
        "description": "User asks to lengthen a 780 mm shirt to 900 mm with no extra fabric. The length gate fails with a -150 mm residual; the engine offers a supported crop instead.",
        "project": project(key, f"msr-{key}", f"job-{key}"),
        "garment": garment(key, "woven_shirt", "woven", ["button_placket", "curved_hem"]),
        "measurements": measurements(key, SHIRT_DIMS, [], []),
        "inspiration": inspiration(key, "Make this shirt into a longer shirt dress.", {"transformation": "lengthen", "target_finished_length_mm": 900}),
        "job": job(key, "complete", ["des-longer-a"], "no_feasible_design"),
        "designs": {
            "project_id": f"prj-{key}",
            "job_id": f"job-{key}",
            "designs": [candidate(rev, 1, "Longer shirt dress, 900 mm", explanation, ["back_panel", "front_left", "front_right"])],
            "binding_constraint": check,
        },
        "revisions": [rev],
        "cut_plan": None,
        "diy_steps": None,
        "quotes": [],
        "evidence": [],
    }


def needs_input() -> dict[str, Any]:
    key = "unsure"
    dims = {
        "shoulder_to_hem": mv(760, origin="vision_suggested", confirmed=None, entered_unit="mm"),
        "chest_flat_width": mv(550),
    }
    issues = [{"dimension": "shoulder_to_hem", "code": "UNCONFIRMED_DIMENSION", "message": "Measure shoulder to hem with a tape and confirm the value."}]
    params = {"finished_length_mm": 500, "hem_allowance_mm": 30, "hem_finish": "double_fold"}
    check = checks(
        False,
        [
            ("supported_material", "pass", None),
            ("required_dimensions", "needs_input", "UNCONFIRMED_DIMENSION"),
            ("length_gate", "not_run", None),
            ("structure", "not_run", None),
            ("construction", "not_run", None),
        ],
        missing=["shoulder_to_hem"],
    )
    rev = revision(
        key, "unsure-a", 1, category="woven_shirt", fabric="woven", recipe_id=CROP, parameters=params,
        geometry={}, check=check, status="NEEDS_INPUT", diy=None, pending=[], measurements_id=f"msr-{key}",
    )
    explanation = "We need a confirmed shoulder-to-hem length before we can check this crop. The photo suggestion has not been confirmed with a tape."
    return {
        "mock": True,
        "scenario": "needs_input",
        "description": "Crop request where shoulder_to_hem is only a vision suggestion with confirmed_at = null, so the engine returns NEEDS_INPUT and computes no geometry.",
        "project": project(key, f"msr-{key}", f"job-{key}"),
        "garment": garment(key, "woven_shirt", "woven", ["button_placket"]),
        "measurements": measurements(key, dims, issues, ["shoulder_to_hem"]),
        "inspiration": inspiration(key, "Crop it to just above the waist.", {"transformation": "crop", "target_finished_length_mm": 500}),
        "job": job(key, "complete", ["des-unsure-a"], "needs_input"),
        "designs": {
            "project_id": f"prj-{key}",
            "job_id": f"job-{key}",
            "designs": [candidate(rev, 1, "Cropped shirt, 500 mm", explanation, ["back_panel", "front_left", "front_right"])],
            "binding_constraint": None,
        },
        "revisions": [rev],
        "cut_plan": None,
        "diy_steps": None,
        "quotes": [],
        "evidence": [],
    }


def idea_only() -> dict[str, Any]:
    key = "idea"
    check = checks(False, [("supported_recipe", "fail", "UNSUPPORTED_RECIPE")])
    rev = revision(
        key, "idea-a", 1, category="jersey_tee", fabric="knit", recipe_id=None, parameters={},
        geometry={}, check=check, status="IDEA_ONLY", diy="TAILOR_RECOMMENDED", pending=[],
        measurements_id=f"msr-{key}", preview_kind="concept_image",
    )
    explanation = "A boned corset top from a jersey tee is outside our reviewed recipes. You can keep it as an idea or ask a tailor; we cannot give a cut plan."
    dims = {"shoulder_to_hem": mv(700), "chest_flat_width": mv(520)}
    maker_request = {
        "request_id": "req-idea-a-1",
        "user_id": "usr-demo-01",
        "tailor_id": "usr-tailor-01",
        "revision_id": "rev-idea-a-1",
        "brief": {
            "verification_label": "inspiration_only",
            "design_status": "IDEA_ONLY",
            "garment_category": "jersey_tee",
            "modification_request": "Turn this tee into a fitted corset-style top. Inspiration only; nothing has been checked.",
            "shared_photo_ids": ["pho-idea-front"],
            "shared_measurements": {},
            "unresolved_checks": ["No reviewed recipe; construction and fit are unchecked."],
            "consent": {"consent_version": "2026-10-draft", "shared_fields": ["garment_category", "photos.front"], "consented_at": T2},
        },
        "status": "DRAFT",
        "price_estimate": None,
        "created_at": T2,
        "updated_at": T2,
    }
    return {
        "mock": True,
        "scenario": "idea_only",
        "description": "Knit tee to boned corset top: no reviewed recipe exists, so the design is IDEA_ONLY with no recipe, geometry or cut plan, and the tailor brief is labelled inspiration_only.",
        "project": project(key, f"msr-{key}", f"job-{key}"),
        "garment": garment(key, "jersey_tee", "knit", ["crew_neck", "short_sleeves"]),
        "measurements": measurements(key, dims, [], []),
        "inspiration": inspiration(key, "Turn this into a corset top with boning.", {"transformation": "other", "waist_shaping": True}),
        "job": job(key, "complete", ["des-idea-a"], "unsupported"),
        "designs": {
            "project_id": f"prj-{key}",
            "job_id": f"job-{key}",
            "designs": [candidate(rev, 1, "Corset-style top (idea)", explanation, [])],
            "binding_constraint": None,
        },
        "revisions": [rev],
        "cut_plan": None,
        "diy_steps": None,
        "maker_request": maker_request,
        "quotes": [],
        "evidence": [],
    }


def job_failed_no_designs() -> dict[str, Any]:
    key = "timeout"
    error = {
        "code": "MODEL_TIMEOUT",
        "message": "Design generation took too long. Your inputs are saved; try again.",
        "recoverable": True,
        "retry_after_s": 30,
        "field_errors": [],
        "request_id": "mock-req-0001",
    }
    return {
        "mock": True,
        "scenario": "job_failed_no_designs",
        "description": "Generation job failed with a recoverable error and the design list is empty. Covers the zero-candidate and failed-job edge states.",
        "project": project(key, f"msr-{key}", f"job-{key}"),
        "garment": garment(key, "woven_shirt", "woven", ["button_placket"]),
        "measurements": measurements(key, SHIRT_DIMS, [], []),
        "job": job(key, "failed", None, error=error),
        "designs": {"project_id": f"prj-{key}", "job_id": f"job-{key}", "designs": [], "binding_constraint": None},
        "revisions": [],
        "cut_plan": None,
        "diy_steps": None,
        "quotes": [],
        "evidence": [],
    }


def main() -> None:
    FIXTURES.mkdir(exist_ok=True)
    for build in [woven_shirt_crop_pass, lengthening_impossible, needs_input, idea_only, job_failed_no_designs]:
        fx = copy.deepcopy(build())
        path = FIXTURES / f"{fx['scenario']}.json"
        path.write_text(json.dumps(fx, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
