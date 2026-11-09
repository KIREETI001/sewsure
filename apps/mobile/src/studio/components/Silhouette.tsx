import { StyleSheet, View } from "react-native";
import { Text, useTheme } from "../../../ui";
import { t } from "@/i18n";
import { formatCm } from "../format";
import type { DesignRevision } from "../types";

const HEIGHT = 180;
const WIDTH = 120;

/**
 * Approximate 2D outline drawn from the revision's geometry_mm (numbers supplied by the engine).
 * Plain Views only. Always labelled approximate; never a cutting guide.
 */
export function Silhouette({ revision }: { revision: DesignRevision }) {
  const { colors } = useTheme();
  const preview = revision.preview;
  const original = revision.geometry_mm.original_length_mm;
  const finished = revision.geometry_mm.finished_length_mm;
  const cutMark = revision.geometry_mm.cut_mark_from_shoulder_mm;

  let body: React.ReactNode;
  if (preview?.kind === "concept_image") {
    body = <Text tone="secondary">{t("studio.silhouette.concept")}</Text>;
  } else if (!original || finished === undefined) {
    body = <Text tone="secondary">{t("studio.silhouette.none")}</Text>;
  } else {
    const scale = HEIGHT / Math.max(original, cutMark ?? finished);
    const originalH = original * scale;
    const finishedH = finished * scale;
    const cutH = (cutMark ?? finished) * scale;
    body = (
      <View
        accessible
        accessibilityRole="image"
        accessibilityLabel={t("studio.silhouette.a11y", {
          finished: formatCm(finished),
          original: formatCm(original),
        })}
        style={styles.row}
      >
        <View style={{ width: WIDTH + 40, height: HEIGHT + 8 }}>
          <View style={[styles.sleeve, { left: 0, borderColor: colors.border }]} />
          <View style={[styles.sleeve, { right: 0, borderColor: colors.border }]} />
          <View
            style={[styles.outline, { height: originalH, borderColor: colors.border, left: 20 }]}
          />
          <View
            style={[
              styles.fill,
              { height: finishedH, backgroundColor: colors.primary, left: 20, opacity: 0.35 },
            ]}
          />
          <View style={[styles.cut, { top: cutH, borderColor: colors.text, left: 12 }]} />
        </View>
        <View style={styles.legend}>
          <Text variant="caption">{`■ ${t("studio.silhouette.finished", { length: formatCm(finished) })}`}</Text>
          <Text variant="caption">{`┄ ${t("studio.silhouette.removed")}`}</Text>
          {cutMark !== undefined ? (
            <Text variant="caption">{`— ${t("studio.silhouette.cut", { length: formatCm(cutMark) })}`}</Text>
          ) : null}
        </View>
      </View>
    );
  }
  return (
    <View style={styles.wrap}>
      <Text variant="heading" accessibilityRole="header">
        {t("studio.silhouette.title")}
      </Text>
      {body}
      <Text variant="caption" tone="secondary">
        {t("studio.silhouette.label")}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: 8 },
  row: { flexDirection: "row", gap: 16, alignItems: "flex-start" },
  legend: { flex: 1, gap: 4 },
  outline: { position: "absolute", top: 0, width: WIDTH, borderWidth: 2, borderStyle: "dashed" },
  fill: { position: "absolute", top: 0, width: WIDTH },
  sleeve: {
    position: "absolute",
    top: 0,
    width: 22,
    height: 60,
    borderWidth: 2,
    borderStyle: "dashed",
  },
  cut: { position: "absolute", width: WIDTH + 16, borderTopWidth: 2 },
});
