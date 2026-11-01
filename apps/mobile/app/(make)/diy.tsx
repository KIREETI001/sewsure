import { useLocalSearchParams, useRouter } from "expo-router";
import { useEffect } from "react";
import { View } from "react-native";
import { Button, ChecklistItem, StepCard, Text } from "../../ui";
import { CheckpointList } from "@/make/components/CheckpointList";
import { BlockedGuide, DraftBanner, GateNotice, LoadFailed, Loading, Page } from "@/make/components/Shell";
import { blockedReason, checkpointsComplete, cutGuideAccess, guideMode, resolveSteps } from "@/make/gate";
import { tm } from "@/make/i18n";
import { useMakeStore } from "@/make/store";
import { goBack } from "@/make/nav";
import { revisionIdParam, useMakeBundle } from "@/make/useMakeBundle";

export default function DiyScreen() {
  const params = useLocalSearchParams<{ revisionId?: string | string[] }>();
  const revisionId = revisionIdParam(params.revisionId);
  const router = useRouter();
  const q = useMakeBundle(revisionId);
  const b = q.data ?? undefined;
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

  if (!revisionId) return <GateNotice reason="no_revision" onBack={() => goBack(router)} />;
  // A cached bundle is not trusted while a refetch runs: the revision may have been superseded.
  if (q.isLoading || (q.isFetching && !q.isError)) return <Loading />;
  if (q.isError) return <LoadFailed onRetry={() => void q.refetch()} />;
  if (q.data === null) return <GateNotice reason="not_found" onBack={() => goBack(router)} />;
  if (!b) return <Loading />;
  const { cutPlan, diySteps } = b;
  const access = cutGuideAccess(b.revision, cutPlan);
  if (!access.allowed || !cutPlan || !diySteps) {
    return (
      <Page bundle={b}>
        <Text testID="gate-reason">{tm(`make.gate.reason.${access.allowed ? "no_plan" : access.reason}` as const)}</Text>
        <Button variant="secondary" label={tm("make.back")} onPress={() => goBack(router)} />
      </Page>
    );
  }
  const mode = guideMode(diySteps, cutPlan, b.provenance);
  if (mode === "blocked") {
    return (
      <Page bundle={b}>
        <BlockedGuide reason={blockedReason(diySteps, cutPlan)} onBack={() => goBack(router)} />
      </Page>
    );
  }

  const same = mine !== undefined && mine.cutPlanId === planId;
  const cpDone = checkpointsComplete(cutPlan, same ? mine.checkpoints : {});
  const resolved = resolveSteps(diySteps.steps, cpDone, same ? mine.steps : {});
  const doneCount = resolved.filter((r) => r.done).length;
  const next = resolved.find((r) => !r.done)?.step;
  const checkpointOrder = resolved.find((r) => r.step.phase === "ruler_checkpoint")?.step.order ?? "";
  const bodyOf = (r: (typeof resolved)[number]) => {
    const parts: string[] = [];
    if (mode === "demo_preview" && r.step.irreversible) parts.push(tm("make.draft.step"));
    if (r.lock === "checkpoint_required") parts.push(tm("make.diy.lockedCheckpoint", { n: checkpointOrder }));
    else if (r.lock === "cut_required") parts.push(tm("make.diy.lockedCut"));
    else parts.push(r.step.body);
    if (r.step.irreversible) parts.push(tm("make.diy.irreversible"));
    return parts.join(" ");
  };

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
      <Text testID="progress-count">{tm("make.diy.progress", { done: doneCount, total: resolved.length })}</Text>
      {next && doneCount > 0 ? (
        <Text testID="resume-banner" variant="bodyStrong">
          {tm("make.diy.resume", { n: next.order, title: next.title })}
        </Text>
      ) : null}
      {resolved.map((r) => (
        // Controls sit beside the card, not inside it: StepCard is one accessible element, so
        // children inside it are not reachable by a screen reader.
        <View key={r.step.step_id} style={{ gap: 8 }}>
          <StepCard
            stepNumber={r.step.order}
            totalSteps={resolved.length}
            title={r.step.title}
            body={bodyOf(r)}
            done={r.done}
          />
          {r.step.phase === "ruler_checkpoint" ? (
            <>
              <Text tone="secondary">{tm("make.diy.checkpointStep")}</Text>
              <CheckpointList revisionId={rid} cutPlan={cutPlan} />
            </>
          ) : (
            <ChecklistItem
              label={`${tm("make.diy.tick")}: ${r.step.title}`}
              checked={r.done}
              disabled={r.lock !== null}
              onToggle={(v) => {
                if (r.lock === null) setStep(rid, planId, r.step.step_id, v);
              }}
            />
          )}
        </View>
      ))}
    </Page>
  );
}
