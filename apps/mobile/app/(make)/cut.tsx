import { useLocalSearchParams, useRouter } from "expo-router";
import { Button, StateBadge, Text } from "../../ui";
import { CheckpointList } from "@/make/components/CheckpointList";
import { DimensionedDiagram } from "@/make/components/DimensionedDiagram";
import { PhotoOverlay } from "@/make/components/PhotoOverlay";
import { DraftBanner, LoadFailed, Loading, Page } from "@/make/components/Shell";
import { cutGuideAccess, guideMode, overlayDecision } from "@/make/gate";
import { tm } from "@/make/i18n";
import { useMakeBundle } from "@/make/useMakeBundle";

export default function CutScreen() {
  const { revisionId } = useLocalSearchParams<{ revisionId?: string }>();
  const router = useRouter();
  const q = useMakeBundle(revisionId);
  if (q.isLoading) return <Loading />;
  if (q.isError || !q.data) return <LoadFailed onRetry={() => void q.refetch()} />;
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
        <Button variant="secondary" label={tm("make.back")} onPress={() => router.back()} />
      </Page>
    );
  }

  const mode = guideMode(b.diySteps, b.cutPlan, b.provenance);
  if (mode === "blocked") {
    return (
      <Page bundle={b}>
        <Text testID="draft-blocked">{tm("make.draft.blocked")}</Text>
      </Page>
    );
  }
  const decision = overlayDecision(b.cutPlan, b.photo);
  // The contract has no fetchable photo URL yet, so an overlay also needs one from the API.
  const uri = (b.photo as { url?: string } | null)?.url;
  return (
    <Page bundle={b}>
      <StateBadge state={b.revision.status} />
      {mode === "demo_preview" ? <DraftBanner /> : null}
      <Text>{tm("make.cut.approx")}</Text>
      <CheckpointList revisionId={b.revision.revision_id} cutPlan={b.cutPlan} />
      {decision.kind === "overlay" && b.photo && uri ? (
        <PhotoOverlay
          plan={b.cutPlan}
          photo={b.photo}
          uri={uri}
          projection={decision.projection}
          toleranceMm={b.cutPlan.calibration.tolerance_mm ?? 0}
        />
      ) : (
        <>
          <Text variant="bodyStrong" testID="fallback-heading">
            {tm("make.cut.fallbackHeading")}
          </Text>
          <Text>
            {tm(`make.cut.fallback.${decision.kind === "diagram" ? decision.reason : "missing_projection"}` as const)}
          </Text>
          {decision.kind === "diagram" && decision.apiReason ? (
            <Text tone="secondary">{tm("make.cut.fallbackApiReason", { reason: decision.apiReason })}</Text>
          ) : null}
        </>
      )}
      <DimensionedDiagram plan={b.cutPlan} />
      <Button
        label={tm("make.cut.continue")}
        onPress={() => router.push({ pathname: "/diy", params: { revisionId: b.revision.revision_id } })}
      />
    </Page>
  );
}
