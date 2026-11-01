import { useQuery } from "@tanstack/react-query";
import { View } from "react-native";
import { getStudioApi } from "@/api/studio";
import { t } from "@/i18n";
import { Button, Card, MockBadge, StateBadge, Text } from "../../../ui";
import { dimensionText, failureText, flagText, tOr } from "../format";
import type { DesignCandidate } from "../types";

export function CandidateCard({ design, onView }: { design: DesignCandidate; onView: () => void }) {
  const api = getStudioApi();
  const rev = useQuery({
    queryKey: ["revision", design.current_revision_id],
    queryFn: () => api.getRevision(design.current_revision_id),
  });
  const revision = rev.data?.data;
  const compromises = [
    ...(revision?.checks.uncertainty_flags ?? []).map(flagText),
    ...(revision?.pending_checks ?? []),
  ];
  const reasons = [
    ...(design.failure_codes ?? []).map(failureText),
    ...(design.missing_dimensions?.length
      ? [
          t("studio.results.missing", {
            fields: design.missing_dimensions.map(dimensionText).join(", "),
          }),
        ]
      : []),
  ];
  const mocked = design.provenance.source === "mock" || rev.data?.provenance === "mock";
  return (
    <Card>
      <Text variant="label" tone="secondary">
        {t("studio.results.rank", { rank: design.rank })}
      </Text>
      <Text variant="heading" accessibilityRole="header">
        {design.title}
      </Text>
      <StateBadge state={design.status} />
      {mocked ? <MockBadge /> : null}
      <Text>{design.explanation}</Text>
      {reasons.map((r) => (
        <Text key={r}>{`• ${r}`}</Text>
      ))}
      <Text variant="label">{t("studio.results.compromises")}</Text>
      {rev.isPending ? <Text tone="secondary">{t("studio.results.diyLoading")}</Text> : null}
      {revision && compromises.length === 0 ? (
        <Text tone="secondary">{t("studio.results.noCompromises")}</Text>
      ) : null}
      {compromises.map((c) => (
        <Text key={c}>{`• ${c}`}</Text>
      ))}
      <View>
        <Text variant="label">{t("studio.results.diy")}</Text>
        <Text>
          {tOr(`studio.diy.${revision?.diy_suitability ?? "none"}`, t("studio.diy.none"))}
        </Text>
      </View>
      <Button
        label={t("studio.results.view")}
        accessibilityLabel={t("studio.results.viewA11y", { title: design.title })}
        onPress={onView}
      />
    </Card>
  );
}
