import { useQuery } from "@tanstack/react-query";
import { useRouter } from "expo-router";
import { ScrollView, View } from "react-native";
import { getStudioApi } from "@/api/studio";
import { t, type MessageKey } from "@/i18n";
import { useStudioStore } from "@/state/studioStore";
import { CandidateCard } from "@/studio/components/CandidateCard";
import { failureText, formatCm, geometryLabel } from "@/studio/format";
import type { ConstraintResult, JobResult } from "@/studio/types";
import { Button, Card, MockBadge, Text, ThemeProvider } from "../../ui";

function BindingConstraint({ constraint }: { constraint: ConstraintResult }) {
  const worst = [...constraint.residuals].sort((a, b) => a.residual_mm - b.residual_mm)[0];
  return (
    <View style={{ gap: 6 }}>
      <Text variant="heading" accessibilityRole="header">
        {t("studio.zero.binding")}
      </Text>
      {constraint.failure_codes.map((c) => (
        <Text key={c}>{`✗ ${failureText(c)}`}</Text>
      ))}
      {worst && worst.residual_mm < 0 ? (
        <Text>
          {t("studio.zero.shortBy", {
            required: formatCm(worst.required_mm),
            available: formatCm(worst.available_mm),
            short: formatCm(-worst.residual_mm),
          })}
        </Text>
      ) : null}
      {(constraint.alternatives ?? []).length ? (
        <>
          <Text variant="label">{t("studio.zero.alternativesHeading")}</Text>
          {(constraint.alternatives ?? []).map((a) => (
            <Text key={a.reason}>{`• ${a.reason} (${Object.entries(a.parameters)
              .filter(([k]) => k.endsWith("_mm"))
              .map(([k, v]) => `${geometryLabel(k)} ${formatCm(Number(v))}`)
              .join(", ")})`}</Text>
          ))}
        </>
      ) : null}
    </View>
  );
}

export default function ResultsScreen() {
  const router = useRouter();
  const api = getStudioApi();
  const projectId = useStudioStore((s) => s.projectId) ?? "mock-project";
  const jobId = useStudioStore((s) => s.jobId);
  const list = useQuery({
    queryKey: ["designs", projectId],
    queryFn: () => api.listDesigns(projectId),
  });
  const job = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => api.getJob(jobId as string),
    enabled: Boolean(jobId),
  });

  const designs = [...(list.data?.data.designs ?? [])].sort((a, b) => a.rank - b.rank);
  const outcome: JobResult["outcome"] =
    job.data?.data.result?.outcome ?? (designs.length ? "designs" : "no_feasible_design");
  const binding = list.data?.data.binding_constraint ?? null;
  const showZero = designs.length === 0 || outcome !== "designs";

  return (
    <ThemeProvider>
      <ScrollView contentContainerStyle={{ padding: 16, gap: 12 }}>
        {list.data?.provenance === "mock" ? <MockBadge /> : null}
        <Text variant="title" accessibilityRole="header">
          {t("studio.results.title")}
        </Text>
        {list.isPending ? <Text>{t("studio.results.loading")}</Text> : null}
        {list.isError ? (
          <View style={{ gap: 8 }}>
            <Text tone="danger" accessibilityRole="alert">{`! ${t("studio.results.failed")}`}</Text>
            <Button label={t("common.retry")} onPress={() => void list.refetch()} />
          </View>
        ) : null}
        {list.data ? (
          <>
            {showZero ? (
              <Card>
                <Text variant="heading" accessibilityRole="header">
                  {t("studio.zero.title")}
                </Text>
                <Text>{t(`studio.zero.outcome.${outcome}` as MessageKey)}</Text>
                {binding ? <BindingConstraint constraint={binding} /> : null}
                <Text variant="heading" accessibilityRole="header">
                  {t("studio.zero.nextStep")}
                </Text>
                <Text>{t("studio.zero.nextStepBody")}</Text>
                <Button
                  label={t("studio.results.edit")}
                  onPress={() => router.push("/inspiration")}
                />
              </Card>
            ) : null}
            {designs.length > 0 ? (
              <Text accessibilityRole="header">
                {designs.length === 1
                  ? t("studio.results.count.one")
                  : t("studio.results.count.other", { count: designs.length })}
              </Text>
            ) : null}
            {designs.map((d) => (
              <CandidateCard
                key={d.design_id}
                design={d}
                onView={() =>
                  router.push({ pathname: "/design", params: { designId: d.design_id } })
                }
              />
            ))}
          </>
        ) : null}
      </ScrollView>
    </ThemeProvider>
  );
}
