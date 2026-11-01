/**
 * Studio record types. Type-only re-exports of the generated contract
 * (packages/contracts/generated/ts/sewsure.v1.ts), so nothing here can drift from the contract
 * and nothing is bundled at runtime. Contract changes happen in packages/contracts only.
 */
import type { components } from "../../../../packages/contracts/generated/ts/sewsure.v1";

type Schemas = components["schemas"];

export type DesignState = Schemas["DesignState"];
export type Job = Schemas["Job"];
export type JobResult = Schemas["Job"] extends { result?: infer R } ? NonNullable<R> : never;
export type ApiErrorBody = Schemas["ApiError"];
export type DesignCandidate = Schemas["DesignCandidate"];
export type DesignList = Schemas["DesignList"];
export type DesignRevision = Schemas["DesignRevision"];
export type RevisionCreate = Schemas["RevisionCreate"];
export type ConstraintResult = Schemas["ConstraintResult"];
export type FitAssessment = Schemas["FitAssessment"];
export type Parameters = Schemas["DesignRevision"]["parameters"];
