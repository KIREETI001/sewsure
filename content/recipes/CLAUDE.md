# content/recipes

Owner: Narthananilaa. Agent: N5 Recipe Author. Display work by D4.

One folder per recipe, for example `woven_shirt_crop_v1/`, containing `recipe.yaml`, diagrams and `rights.yaml`.

## recipe.yaml fields (§8.1)

`recipe_id`, `version`, `status` (`draft` | `reviewed` | `retired`), `eligibility`, `required_tools`, `skill_prerequisites`, `materials`, `steps` (each with `id`, `text`, `checkpoint` flag), `evidence_links`, `difficulty`, `reviewed_by`, `reviewed_on`.

## Rules

- Agents may only create or edit recipes with `status: draft`. Moving to `reviewed` needs a named human sewist and a date (H-02).
- Released versions are immutable. Changes create a new version.
- Every irreversible step (cut, trim) is preceded by a ruler checkpoint step.
- Any third-party photo, video or diagram needs an entry in `rights.yaml`. No entry, no media.
- Start with 4–6 technique micro-lessons tied to supported transformations.
