import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useState } from "react";
import { ScrollView, View } from "react-native";
import { getStudioApi } from "@/api/studio";
import { t, type MessageKey } from "@/i18n";
import { newIdempotencyKey, useStudioStore } from "@/state/studioStore";
import { FitSummary } from "@/studio/components/FitSummary";
import { Silhouette } from "@/studio/components/Silhouette";
import { editableAttributes, readOnlyParameters } from "@/studio/editable";
import { StudioApiError } from "@/studio/errors";
import { dimensionText, failureText, flagText, mmToCmText, tOr } from "@/studio/format";
import { canOpenCutGuide, isStale } from "@/studio/stale";
import { invalidateMake } from "@/make/useMakeBundle";
import type { DesignRevision } from "@/studio/types";
import {
  Button,
  Card,
  MeasurementInput,
  MockBadge,
  parseCmToMm,
  StateBadge,
  Text,
  ThemeProvider,
} from "../../ui";

const CHECK_SYMBOL: Record<string, string> = {
  pass: "✓",
  fail: "✗",
  needs_input: "?",
  not_applicable: "–",
  not_run: "○",
};

export default function DesignScreen() {
  const router = useRouter();
  const qc = useQueryClient();
  const api = getStudioApi();
  const { designId = "", revisionId } = useLocalSearchParams<{
    designId?: string;
    revisionId?: string;
  }>();
  const projectId = useStudioStore((s) => s.projectId) ?? "mock-project";
  const drafts = useStudioStore((s) => s.editDrafts[designId]);
  const [viewId, setViewId] = useState<string | null>(revisionId ?? null);
  const [editError, setEditError] = useState<"failed" | "conflict" | null>(null);

  const list = useQuery({
    queryKey: ["designs", projectId],
    queryFn: () => api.listDesigns(projectId),
  });
  const design = list.data?.data.designs.find((d) => d.design_id === designId);
  const currentId = design?.current_revision_id ?? null;
  const shownId = viewId ?? currentId;

  const rev = useQuery({
    queryKey: ["revision", shownId],
    queryFn: () => api.getRevision(shownId as string),
    enabled: Boolean(shownId),
  });
  const chain = useQuery({
    queryKey: ["chain", currentId],
    enabled: Boolean(currentId),
    queryFn: async () => {
      const out: DesignRevision[] = [];
      let id: string | null = currentId;
      while (id && out.length < 10) {
        const r: DesignRevision = (await api.getRevision(id)).data;
        out.push(r);
        id = r.parent_revision_id;
      }
      return out;
    },
  });

  const revision = rev.data?.data;
  const readOnly = revision?.status === "SUPERSEDED";
  const stale = Boolean(revision) && !readOnly && isStale(revision as DesignRevision);
  const isCurrent = revision?.revision_id === currentId;
  const attrs = revision ? editableAttributes(revision.recipe_id, revision.parameters) : [];
  const text = (key: string, mm: number) => drafts?.[key] ?? mmToCmText(mm);

  const changed: Record<string, number> = {};
  let invalid = false;
  if (revision) {
    for (const a of attrs) {
      const current = Number(revision.parameters[a.key]);
      const p = parseCmToMm(text(a.key, current));
      if (p.status !== "ok") invalid = true;
      else if (p.mm !== current) changed[a.key] = p.mm;
    }
  }

  const recheck = useMutation({
    mutationFn: (parameters: Record<string, number> = changed) =>
      api.createRevision(
        designId,
        {
          parent_revision_id: (revision as DesignRevision).revision_id,
          parameters: parameters as unknown as DesignRevision["parameters"],
        },
        { idempotencyKey: newIdempotencyKey() },
      ),
    onSuccess: async (res) => {
      await invalidateMake(qc, revision?.revision_id ?? "", res.data.revision_id);
      useStudioStore.getState().clearEditDraft(designId);
      setEditError(null);
      qc.setQueryData(["revision", res.data.revision_id], res);
      await qc.invalidateQueries({ queryKey: ["designs", projectId] });
      await qc.invalidateQueries({ queryKey: ["chain"] });
      await qc.invalidateQueries({ queryKey: ["revision"] });
      setViewId(null);
    },
    onError: (e) =>
      setEditError(e instanceof StudioApiError && e.status === 409 ? "conflict" : "failed"),
  });

  const reload = async () => {
    setEditError(null);
    await qc.invalidateQueries();
    setViewId(null);
  };

  const lastPassed = (chain.data ?? []).find((r) => r.checks.hard_pass);
  const fixed = revision ? readOnlyParameters(revision.recipe_id, revision.parameters) : [];

  return (
    <ThemeProvider>
      <ScrollView contentContainerStyle={{ padding: 16, gap: 12 }}>
        {rev.data?.provenance === "mock" ? <MockBadge /> : null}
        {list.isPending || (rev.isPending && shownId) ? (
          <Text>{t("studio.design.loading")}</Text>
        ) : null}
        {list.data && !design ? <Text>{t("studio.design.notFound")}</Text> : null}
        {list.isError || rev.isError ? (
          <View style={{ gap: 8 }}>
            <Text tone="danger" accessibilityRole="alert">{`! ${t("studio.design.failed")}`}</Text>
            <Button label={t("common.retry")} onPress={() => void reload()} />
          </View>
        ) : null}
        {design && revision ? (
          <>
            <Text variant="title" accessibilityRole="header">
              {design.title}
            </Text>
            <StateBadge state={revision.status} />
            <Text variant="caption" tone="secondary">
              {t(isCurrent ? "studio.design.versionCurrent" : "studio.design.version", {
                number: revision.revision_number,
              })}
            </Text>
            {readOnly ? (
              <Card>
                <Text variant="heading">{`↺ ${t("studio.design.supersededTitle")}`}</Text>
                <Text>{t("studio.design.supersededBody")}</Text>
                <Button label={t("studio.design.openCurrent")} onPress={() => setViewId(null)} />
              </Card>
            ) : null}
            {stale ? (
              <Card>
                <Text variant="heading">{`! ${t("studio.stale.title")}`}</Text>
                <Text>{t("studio.stale.body")}</Text>
                {editError ? (
                  <Text
                    tone="danger"
                    accessibilityRole="alert"
                  >{`! ${t("studio.stale.failed")}`}</Text>
                ) : null}
                <Button
                  label={t("studio.stale.recheck")}
                  loading={recheck.isPending}
                  onPress={() => recheck.mutate({})}
                />
              </Card>
            ) : null}
            <Text>{design.explanation}</Text>
            {stale ? (
              <Text tone="secondary">{t("studio.stale.hidden")}</Text>
            ) : (
              <>
                <Silhouette revision={revision} />
                <FitSummary revision={revision} />
              </>
            )}
            {canOpenCutGuide(revision) ? (
              <Button
                label={t("studio.cut.open")}
                onPress={() =>
                  router.push({ pathname: "/cut", params: { revisionId: revision.revision_id } })
                }
              />
            ) : null}

            <Text variant="heading" accessibilityRole="header">
              {t("studio.design.checks")}
            </Text>
            {revision.checks.checks.map((c) => (
              <Text key={c.check_id}>
                {`${CHECK_SYMBOL[c.result] ?? "•"} ${c.check_id.replace(/_/g, " ")}: ${t(
                  `studio.design.check.${c.result}` as MessageKey,
                )}`}
              </Text>
            ))}
            {revision.checks.failure_codes.map((c) => (
              <Text key={c}>{`✗ ${failureText(c)}`}</Text>
            ))}
            {revision.checks.missing_dimensions.map((d) => (
              <Text key={d}>{`? ${dimensionText(d)}`}</Text>
            ))}
            {revision.checks.uncertainty_flags.map((f) => (
              <Text key={f}>{`! ${flagText(f)}`}</Text>
            ))}
            <Text>
              {tOr(`studio.diy.${revision.diy_suitability ?? "none"}`, t("studio.diy.none"))}
            </Text>
            {revision.pending_checks.length ? (
              <>
                <Text variant="heading" accessibilityRole="header">
                  {t("studio.design.beforeCutting")}
                </Text>
                {revision.pending_checks.map((p) => (
                  <Text key={p}>{`• ${p}`}</Text>
                ))}
              </>
            ) : null}

            <Text variant="heading" accessibilityRole="header">
              {t("studio.edit.title")}
            </Text>
            {readOnly ? (
              <Button
                label={t("studio.design.reuse")}
                variant="secondary"
                onPress={() => {
                  useStudioStore
                    .getState()
                    .setEditDraft(
                      designId,
                      Object.fromEntries(
                        attrs.map((a) => [a.key, mmToCmText(Number(revision.parameters[a.key]))]),
                      ),
                    );
                  setViewId(null);
                }}
              />
            ) : attrs.length === 0 ? (
              <Text>{t("studio.edit.none")}</Text>
            ) : (
              <View style={{ gap: 8 }}>
                <Text>{t("studio.edit.intro")}</Text>
                {attrs.map((a) => {
                  const typed = text(a.key, Number(revision.parameters[a.key]));
                  return (
                    <MeasurementInput
                      key={a.key}
                      label={tOr(`studio.edit.field.${a.key}`, a.key)}
                      text={typed}
                      onChange={({ text: v }) =>
                        useStudioStore.getState().setEditText(designId, a.key, v)
                      }
                      errorText={
                        parseCmToMm(typed).status === "ok" ? undefined : t("studio.edit.invalid")
                      }
                    />
                  );
                })}
                <Text variant="caption" tone="secondary">
                  {t("studio.edit.downstream")}
                </Text>
                {Object.keys(changed).length === 0 && !invalid ? (
                  <Text tone="secondary">{t("studio.edit.unchanged")}</Text>
                ) : null}
                {recheck.isPending ? <Text>{t("studio.edit.rechecking")}</Text> : null}
                {editError ? (
                  <Text tone="danger" accessibilityRole="alert">
                    {`! ${t(editError === "conflict" ? "studio.edit.conflict" : "studio.edit.failed")}`}
                  </Text>
                ) : null}
                {editError === "conflict" ? (
                  <Button
                    label={t("studio.edit.reload")}
                    variant="secondary"
                    onPress={() => void reload()}
                  />
                ) : null}
                <Button
                  label={t("studio.edit.recheck")}
                  loading={recheck.isPending}
                  disabled={invalid || Object.keys(changed).length === 0}
                  onPress={() => recheck.mutate(changed)}
                />
              </View>
            )}
            {fixed.length ? (
              <Text variant="caption" tone="secondary">
                {`${t("studio.edit.readOnlyHeading")}: ${fixed
                  .map(([k, v]) => `${k.replace(/_/g, " ")} ${v}`)
                  .join(", ")}`}
              </Text>
            ) : null}

            <Text variant="heading" accessibilityRole="header">
              {t("studio.design.history")}
            </Text>
            <Text>
              {lastPassed
                ? t("studio.design.lastPassed", { number: lastPassed.revision_number })
                : t("studio.design.noPassed")}
            </Text>
            {(chain.data ?? []).map((r) => (
              <Button
                key={r.revision_id}
                variant="secondary"
                label={t("studio.design.historyOpen", { number: r.revision_number })}
                onPress={() => setViewId(r.revision_id === currentId ? null : r.revision_id)}
              />
            ))}
          </>
        ) : null}
        <Button label={t("studio.design.back")} variant="secondary" onPress={() => router.back()} />
      </ScrollView>
    </ThemeProvider>
  );
}
