"""Local-only Proposer. No photos/measurements in prompts, no geometry from the model."""

import json
from pathlib import Path
from typing import Any
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from sewsure_contracts.ai_candidate_proposal_schema import AiCandidateProposal

from sewsure_api.generation import CROP_RECIPE, Proposal, RuleProposer
from sewsure_api.models import Garment

MODEL_URL = "http://127.0.0.1:8091/v1/chat/completions"
PROMPT_VERSION = "local_recipe_v1"
PROMPT = Path(__file__).resolve().parents[1] / "ai" / "prompts" / f"{PROMPT_VERSION}.md"
# A strict subset of the existing contract, also used for grammar-constrained decoding.
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "proposals": {
            "type": "array",
            "maxItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "recipe_id": {"const": CROP_RECIPE},
                    "parameters": {
                        "type": "object",
                        "properties": {"hem_finish": {"const": "double_fold"}},
                        "required": ["hem_finish"],
                        "additionalProperties": False,
                    },
                },
                "required": ["recipe_id", "parameters"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["proposals"],
    "additionalProperties": False,
}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Local model redirects are forbidden")


class LocalModelProposer:
    """An unavailable/invalid model fails the job. There is no silent mock fallback."""

    def complete(self, text: str) -> str:
        payload = {
            "messages": [
                {"role": "system", "content": PROMPT.read_text(encoding="utf-8")},
                {"role": "user", "content": json.dumps({"synthetic_request": text})},
            ],
            "temperature": 0,
            "max_tokens": 150,
            "response_format": {"type": "json_object", "schema": OUTPUT_SCHEMA},
        }
        # Fixed numeric loopback address, no proxy, no redirects, no credentials.
        request = Request(
            MODEL_URL,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=45) as response:
            if response.geturl() != MODEL_URL:
                raise ValueError("Local model redirected")
            body = json.loads(response.read(65536))
        return body["choices"][0]["message"]["content"]

    def propose(
        self, garment: Garment, measurements: dict[str, Any], inspiration: dict[str, Any]
    ) -> list[Proposal]:
        import jsonschema

        text = inspiration.get("text", "")
        raw = self.complete(text)
        document = json.loads(raw)
        jsonschema.validate(document, OUTPUT_SCHEMA)
        parsed = AiCandidateProposal.model_validate(document)
        transformation = (inspiration.get("requested_features") or {}).get("transformation")
        # Explicit structured intent cannot be overridden by model text. In particular a
        # lengthen request must never become a shortening proposal (or bypass its guard).
        if (
            not parsed.proposals
            or transformation != "crop"
            or garment.category != "woven_shirt"
            or garment.fabric_family != "woven"
        ):
            return [Proposal(None, {}, "Idea only: no supported recipe", transformation)]
        # Target is user input. RuleProposer supplies recipe defaults and preserves intent;
        # evaluate_and_store remains the sole evaluator and cut-plan producer.
        return RuleProposer().propose(garment, measurements, inspiration)
