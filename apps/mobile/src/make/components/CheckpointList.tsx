import { View } from "react-native";
import { ChecklistItem, Text } from "../../../ui";
import { mmToCmText } from "../geometry";
import { tm } from "../i18n";
import { checkpointsComplete } from "../gate";
import { useMakeStore } from "../store";
import type { CutPlan } from "../types";

/** Ruler checkpoints for one cut plan. No skip control exists by design. */
export function CheckpointList({ revisionId, cutPlan, locked }: { revisionId: string; cutPlan: CutPlan; locked: boolean }) {
  const ticked = useMakeStore((s) => s.byRevision[revisionId]);
  const set = useMakeStore((s) => s.setCheckpoint);
  const marks = ticked && ticked.cutPlanId === cutPlan.cut_plan_id ? ticked.checkpoints : {};
  const left = cutPlan.ruler_checkpoints.filter((c) => marks[c.checkpoint_id] !== true).length;
  return (
    <View style={{ gap: 8 }} testID="checkpoint-list">
      <Text variant="heading">{tm("make.cp.heading")}</Text>
      <Text>{tm("make.cp.intro")}</Text>
      {locked ? <Text testID="checkpoints-locked">{tm("make.cp.locked")}</Text> : null}
      {cutPlan.ruler_checkpoints.map((c) => (
        <ChecklistItem
          key={c.checkpoint_id}
          label={tm("make.cp.label", {
            instruction: c.instruction,
            cm: mmToCmText(c.distance_mm),
            landmark: c.from_landmark.replace(/_/g, " "),
            tol: mmToCmText(c.tolerance_mm),
          })}
          checked={marks[c.checkpoint_id] === true}
          disabled={locked}
          onToggle={(v) => !locked && set(revisionId, cutPlan.cut_plan_id, c.checkpoint_id, v)}
        />
      ))}
      <Text tone="secondary">
        {locked ? tm("make.cp.locked") : checkpointsComplete(cutPlan, marks) ? tm("make.cp.done") : tm("make.cp.remaining", { n: left })}
      </Text>
    </View>
  );
}
