import { useLocalSearchParams, useRouter } from "expo-router";
import { useEffect } from "react";
import { View } from "react-native";
import { Button, ChecklistItem, StepCard, Text } from "../../ui";
import { CheckpointList } from "@/make/components/CheckpointList";
import { DraftBanner, LoadFailed, Loading, Page } from "@/make/components/Shell";
import { checkpointsComplete, cutGuideAccess, guideMode, stepLock } from "@/make/gate";
import { tm } from "@/make/i18n";
import { useMakeStore } from "@/make/store";
import { useMakeBundle } from "@/make/useMakeBundle";

export default function DiyScreen() {
  const { revisionId } = useLocalSearchParams<{ revisionId?: string }>();
  const router = useRouter();
  const q = useMakeBundle(revisionId);
  const b = q.data;
  const rid = b?.revision.revision_id ?? "";
  const planId = b?.cutPlan?.cut_plan_id ?? "";
  const mine = useMakeStore((s) => s.byRevision[rid]);
  const hydrated = useMakeStore((s) => s.hydrated);
  const setStep = useMakeStore((s) => s.setStep);
  const seed = useMakeStore((s) => s.seedSteps);

  useEffect(() => {
    if (!b?.serverProgress || !hydrated || !planId) return;
    seed(
      rid,
      planId,
      b.serverProgress.steps.filter((s) => s.self_verification === "self_reported_done").map((s) => s.step_id),
    );
  }, [b, hydrated, planId, rid, seed]);

  if (q.isLoading) return <Loading />;
  if (q.isError || !b) return <LoadFailed onRetry={() => void q.refetch()} />;
  const { cutPlan, diySteps } = b;
  const access = cutGuideAccess(b.revision, cutPlan);
  if (!access.allowed || !cutPlan || !diySteps) {
    return (
      <Page bundle={b}>
        <Text testID="gate-reason">{tm(`make.gate.reason.${access.allowed ? "no_plan" : access.reason}` as const)}</Text>
        <Button variant="secondary" label={tm("make.back")} onPress={() => router.back()} />
      </Page>
    );
  }
  const mode = guideMode(diySteps, cutPlan, b.provenance);
  if (mode === "blocked") {
    return (
      <Page bundle={b}>
        <Text testID="draft-blocked">{tm("make.draft.blocked")}</Text>
      </Page>
    );
  }

  const same = mine !== undefined && mine.cutPlanId === planId;
  const cpDone = checkpointsComplete(cutPlan, same ? mine.checkpoints : {});
  const steps = [...diySteps.steps].sort((a, c) => a.order - c.order);
  const lockedOf = (s: (typeof steps)[number]) => stepLock(s, cpDone) !== null;
  const isDone = (s: (typeof steps)[number]) => !lockedOf(s) && same && mine.steps[s.step_id] === true;
  const doneCount = steps.filter(isDone).length;
  const next = steps.find((s) => !isDone(s));

  return (
    <Page bundle={b}>
      {mode === "demo_preview" ? <DraftBanner /> : null}
      <Text>{tm("make.diy.selfReported")}</Text>
      {diySteps.extra_tools_or_skills_required ? <Text tone="danger">{tm("make.diy.extraRequired")}</Text> : null}
      <Text variant="heading">{tm("make.diy.tools")}</Text>
      <Text>{diySteps.required_tools.join(", ").replace(/_/g, " ")}</Text>
      <Text variant="heading">{tm("make.diy.materials")}</Text>
      <Text>{diySteps.materials.join(", ")}</Text>
      {(diySteps.practice_exercises ?? []).length > 0 ? (
        <View style={{ gap: 8 }}>
          <Text variant="heading">{tm("make.diy.practice")}</Text>
          <Text tone="secondary">{tm("make.diy.practiceNote")}</Text>
          {diySteps.practice_exercises?.map((p, i, all) => (
            <StepCard key={p.step_id} stepNumber={i + 1} totalSteps={all.length} title={p.title} body={p.body} />
          ))}
        </View>
      ) : null}
      <Text testID="progress-count">{tm("make.diy.progress", { done: doneCount, total: steps.length })}</Text>
      {next && doneCount > 0 ? (
        <Text testID="resume-banner" variant="bodyStrong">
          {tm("make.diy.resume", { n: next.order, title: next.title })}
        </Text>
      ) : null}
      {steps.map((s) => (
        <StepCard
          key={s.step_id}
          stepNumber={s.order}
          totalSteps={steps.length}
          title={s.title}
          body={s.body}
          done={isDone(s)}
        >
          {s.irreversible ? <Text tone="danger">{tm("make.diy.irreversible")}</Text> : null}
          {s.phase === "ruler_checkpoint" ? <CheckpointList revisionId={rid} cutPlan={cutPlan} /> : null}
          {lockedOf(s) ? <Text testID={`locked-${s.step_id}`}>{tm("make.diy.lockedCheckpoint")}</Text> : null}
          <ChecklistItem
            label={`${tm("make.diy.tick")}: ${s.title}`}
            checked={isDone(s)}
            disabled={lockedOf(s)}
            onToggle={(v) => setStep(rid, planId, s.step_id, v)}
          />
        </StepCard>
      ))}
    </Page>
  );
}
