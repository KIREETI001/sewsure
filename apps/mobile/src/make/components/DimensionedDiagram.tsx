import { View } from "react-native";
import { Card, Text, useTheme } from "../../../ui";
import { lineDepthMm, lineDepthRangeMm, mmToCmText, mmToInchText, originLandmarkText, planBounds } from "../geometry";
import { tm } from "../i18n";
import type { CutLine, CutPlan } from "../types";

const W = 280;
const H = 160;
const KIND_KEY = {
  cut: "make.cut.kind.cut",
  fold: "make.cut.kind.fold",
  stitch: "make.cut.kind.stitch",
  reference: "make.cut.kind.reference",
} as const;
const DASH = { cut: [1, 0], fold: [8, 6], stitch: [2, 4], reference: [1, 0] } as const;

function Segment({ x1, y1, x2, y2, kind, color }: { x1: number; y1: number; x2: number; y2: number; kind: CutLine["kind"]; color: string }) {
  const len = Math.hypot(x2 - x1, y2 - y1);
  const angle = Math.atan2(y2 - y1, x2 - x1);
  const [on, off] = DASH[kind];
  const n = off === 0 ? 1 : Math.max(1, Math.floor(len / (on + off)));
  const dashes = Array.from({ length: n }, (_, i) => i * (on + off));
  return (
    <>
      {dashes.map((d) => {
        const l = off === 0 ? len : Math.min(on, len - d);
        const cx = x1 + Math.cos(angle) * (d + l / 2);
        const cy = y1 + Math.sin(angle) * (d + l / 2);
        return (
          <View
            key={d}
            style={{ position: "absolute", left: cx - l / 2, top: cy - 1, width: l, height: kind === "reference" ? 1 : 3, backgroundColor: color, transform: [{ rotate: `${angle}rad` }] }}
          />
        );
      })}
    </>
  );
}

/**
 * Plain-language distance for one line, built from the line's kind and its millimetre points
 * (shown in cm), not from the fixture's label text, which can mix units.
 */
export function lineText(l: CutLine, plan: CutPlan): string {
  const landmark = originLandmarkText(plan);
  const depth = lineDepthMm(l);
  const where =
    depth !== null
      ? tm("make.cut.fromLandmark", { cm: mmToCmText(depth), inches: mmToInchText(depth), landmark })
      : tm("make.cut.betweenLandmark", {
          from: mmToCmText(lineDepthRangeMm(l)[0]),
          to: mmToCmText(lineDepthRangeMm(l)[1]),
          landmark,
        });
  return tm("make.cut.lineText", { kind: tm(KIND_KEY[l.kind]), where });
}

/** Always-available fallback: schematic plus plain-language distances for every line. */
export function DimensionedDiagram({ plan }: { plan: CutPlan }) {
  const { colors } = useTheme();
  return (
    <View style={{ gap: 12 }} testID="dimensioned-diagram">
      <Text variant="heading">{tm("make.cut.diagramHeading")}</Text>
      {plan.pieces.map((piece) => {
        const b = planBounds(piece.lines);
        const sx = (W - 16) / Math.max(1, b.maxX - b.minX);
        const sy = (H - 16) / Math.max(1, b.maxY - b.minY);
        const s = Math.min(sx, sy);
        const px = (p: [number, number]): [number, number] => [8 + (p[0] - b.minX) * s, 8 + (p[1] - b.minY) * s];
        return (
          <Card key={piece.piece_id}>
            <Text variant="bodyStrong">{piece.source_panel.replace(/_/g, " ")}</Text>
            <View
              accessible
              accessibilityRole="image"
              accessibilityLabel={tm("make.cut.diagramAlt", { piece: piece.source_panel.replace(/_/g, " ") })}
              style={{ width: W, height: H, borderWidth: 1, borderColor: colors.divider }}
            >
              {piece.lines.map((l) =>
                l.points_mm.slice(1).map((pt, i) => {
                  const [x1, y1] = px(l.points_mm[i] as [number, number]);
                  const [x2, y2] = px(pt as [number, number]);
                  return <Segment key={`${l.line_id}-${i}`} x1={x1} y1={y1} x2={x2} y2={y2} kind={l.kind} color={colors.text} />;
                }),
              )}
            </View>
            {piece.lines.map((l) => (
              <Text key={l.line_id}>{lineText(l, plan)}</Text>
            ))}
            {piece.prohibited_regions?.length ? (
              <Text tone="danger">{tm("make.cut.prohibited", { regions: piece.prohibited_regions.join(", ").replace(/_/g, " ") })}</Text>
            ) : null}
          </Card>
        );
      })}
      <Text>{tm("make.cut.hemAllowance", { cm: mmToCmText(plan.allowances.hem_allowance_mm) })}</Text>
    </View>
  );
}
