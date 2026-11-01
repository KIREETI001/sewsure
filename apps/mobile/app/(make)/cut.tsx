import { useLocalSearchParams, useRouter } from "expo-router";
import { Button, StateBadge, Text } from "../../ui";
import { CheckpointList } from "@/make/components/CheckpointList";
import { DimensionedDiagram } from "@/make/components/DimensionedDiagram";
import { BlockedGuide, DraftBanner, GateNotice, LoadFailed, Loading, Page } from "@/make/components/Shell";
import { blockedReason, cutGuideAccess, guideMode, overlayDecision } from "@/make/gate";
import { tm } from "@/make/i18n";
import { goBack } from "@/make/nav";
import { revisionIdParam, useMakeBundle } from "@/make/useMakeBundle";

export default function CutScreen() {
  const params = useLocalSearchParams<{ revisionId?: string | string[] }>();
  const revisionId = revisionIdParam(params.revisionId);
  const router = useRouter();
  const q = useMakeBundle(revisionId);
  if (!revisionId) return <GateNotice reason="no_revision" onBack={() => goBack(router)} />;
  // A cached bundle is not trusted while a refetch runs: the revision may have been superseded.
  if (q.isLoading || (q.isFetching && !q.isError)) return <Loading />;
  if (q.isError) return <LoadFailed onRetry={() => void q.refetch()} />;
  if (q.data === null) return <GateNotice reason="not_found" onBack={() => goBack(router)} />;
  if (!q.data) return <Loading />;
  const b = q.data;
  const access = cutGuideAccess(b.revision, b.cutPlan);

  if (!access.allowed || !b.cutPlan) {
    const reason = access.allowed ? "no_plan" : access.reason;
    const next = access.allowed ? "go_back" : access.next;
    const newer = access.allowed ? null : access.newerRevisionId;
    return (
      <Page bundle={b}>
        <StateBadge state={b.revision.status} />
        <Text variant="heading">{tm("make.gate.title")}</Text>
        <Text testID="gate-reason">{tm(`make.gate.reason.${reason}` as const)}</Text>
        <Text>{tm(`make.gate.next.${next}` as const)}</Text>
        {newer ? (
          <Button
            label={tm("make.gate.openNewer")}
            onPress={() => router.replace({ pathname: "/cut", params: { revisionId: newer } })}
          />
        ) : null}
        {next === "add_measurements" ? (
          <Button label={tm("make.gate.addMeasurements")} onPress={() => router.push("/(intake)/measurements")} />
        ) : null}
        <Button variant="secondary" label={tm("make.back")} onPress={() => goBack(router)} />
      </Page>
    );
  }

  const mode = guideMode(b.diySteps, b.cutPlan, b.provenance);
  if (mode === "blocked") {
    return (
      <Page bundle={b}>
        <BlockedGuide reason={blockedReason(b.diySteps, b.cutPlan)} onBack={() => goBack(router)} />
      </Page>
    );
  }
  const decision = overlayDecision(b.cutPlan, b.photo);
  return (
    <Page bundle={b}>
      {mode === "demo_preview" ? (
        <>
          <Text variant="bodyStrong" testID="demo-badge">{`⚠ ${tm("make.draft.demoBadge")}`}</Text>
          <DraftBanner />
        </>
      ) : (
        <StateBadge state={b.revision.status} />
      )}
      <Text>{tm("make.cut.approx")}</Text>
      <CheckpointList revisionId={b.revision.revision_id} cutPlan={b.cutPlan} />
      <Text variant="bodyStrong" testID="fallback-heading">
        {tm("make.cut.fallbackHeading")}
      </Text>
      <Text>{tm(`make.cut.fallback.${decision.reason}` as const)}</Text>
      {decision.apiReason ? (
        <Text tone="secondary">{tm("make.cut.fallbackApiReason", { reason: decision.apiReason })}</Text>
      ) : null}
      <DimensionedDiagram plan={b.cutPlan} />
      <Button
        label={tm("make.cut.continue")}
        onPress={() => router.push({ pathname: "/diy", params: { revisionId: b.revision.revision_id } })}
      />
    </Page>
  );
}
