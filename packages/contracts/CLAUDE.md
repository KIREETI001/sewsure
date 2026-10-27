# packages/contracts

Owner: all three (A2 for every change). Primary agent: K1 Contract Architect.

The single source of truth for API routes (§3.4) and records (§3.1): User, Garment, Measurements, Inspiration, DesignCandidate, DesignRevision, CutPlan, DIYProgress, MakerRequest, Quote, EvidenceLog.

## Layout (planned)

```
openapi/sewsure.v1.yaml    OpenAPI 3.1
schemas/*.schema.json      JSON Schema per record and per AI structured output
fixtures/*.json            mock payloads used by mobile and tests; each has "mock": true
CHANGELOG.md               one entry per change: what, why, consumers affected
```

## Rules

- Lengths are mm. Field names end in `_mm` when they hold a length.
- Design state is an enum with exactly the five states in the root CLAUDE.md.
- Lists of candidates allow 0 to 3 items.
- Every change needs a CHANGELOG entry and an updated contract test. Breaking changes bump the version path (`/v2`).
- Generated code (Pydantic models for `services/api`, TypeScript client for `apps/mobile`) is regenerated, never hand-edited.
