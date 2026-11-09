import type { Parameters } from "./types";

/**
 * Attributes the user may edit, per reviewed recipe. This mirrors the recipe's allow-list
 * (content/recipes/<id>/recipe.yaml); the server rejects anything outside it, so this list only
 * decides which inputs to show. A recipe not listed here has no editable attributes, which is
 * also the case for IDEA_ONLY designs (recipe_id null).
 *
 * Only lengths in mm are editable today. `hem_finish` is shown but not editable until the recipe
 * publishes its allowed values.
 */
export interface EditableAttribute {
  key: string;
  kind: "length_mm";
}

const EDITABLE: Record<string, readonly EditableAttribute[]> = {
  woven_shirt_crop_v1: [
    { key: "finished_length_mm", kind: "length_mm" },
    { key: "hem_allowance_mm", kind: "length_mm" },
  ],
};

export const editableAttributes = (
  recipeId: string | null,
  parameters: Parameters,
): readonly EditableAttribute[] => {
  if (!recipeId) return [];
  return (EDITABLE[recipeId] ?? []).filter((a) => typeof parameters[a.key] === "number");
};

/** Parameters shown read-only: present on the revision but not editable. */
export const readOnlyParameters = (
  recipeId: string | null,
  parameters: Parameters,
): [string, number | string | boolean][] => {
  const editable = new Set(editableAttributes(recipeId, parameters).map((a) => a.key));
  return Object.entries(parameters).filter(([k]) => !editable.has(k));
};
