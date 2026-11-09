import { View } from "react-native";
import { Card, Text } from "../../../ui";
import { t } from "@/i18n";
import { formatCm, geometryLabel, tOr } from "../format";
import type { DesignRevision } from "../types";

/** Numeric summary straight from the API: fit assessment when present, else geometry. */
export function FitSummary({ revision }: { revision: DesignRevision }) {
  const geometry = Object.entries(revision.geometry_mm);
  const fit = revision.fit;
  return (
    <Card>
      <Text variant="heading" accessibilityRole="header">
        {t("studio.fit.title")}
      </Text>
      <Text variant="caption" tone="secondary">
        {t("studio.fit.note")}
      </Text>
      {geometry.length === 0 && !fit ? <Text>{t("studio.fit.none")}</Text> : null}
      {geometry.map(([k, mm]) => (
        <View key={k} accessible accessibilityLabel={`${geometryLabel(k)}: ${formatCm(mm)}`}>
          <Text>{`${geometryLabel(k)}: ${formatCm(mm)}`}</Text>
        </View>
      ))}
      {fit ? (
        <>
          <Text variant="bodyStrong">
            {`${t("studio.fit.label")}: ${tOr(`studio.fitLabel.${fit.fit_label}`, fit.fit_label)}`}
          </Text>
          {Object.entries(fit.ease_mm).map(([k, mm]) => (
            <Text
              key={k}
            >{`${t("studio.fit.ease", { name: k.replace(/_/g, " ") })}: ${formatCm(mm)}`}</Text>
          ))}
          {fit.warnings.map((w) => (
            <Text key={w}>{`! ${w}`}</Text>
          ))}
        </>
      ) : null}
    </Card>
  );
}
