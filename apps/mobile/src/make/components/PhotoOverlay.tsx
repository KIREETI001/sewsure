import { Canvas, DashPathEffect, Image as SkImage, Path, Skia, useImage } from "@shopify/react-native-skia";
import { View } from "react-native";
import { Text } from "../../../ui";
import { mmToCmText } from "../geometry";
import type { OverlayProjection } from "../gate";
import { tm } from "../i18n";
import type { CutPlan, PhotoRef } from "../types";

const W = 320;

/** Drawn only after overlayDecision() returned "overlay". Always labelled approximate. */
export function PhotoOverlay({ plan, photo, uri, projection, toleranceMm }: { plan: CutPlan; photo: PhotoRef; uri: string; projection: OverlayProjection; toleranceMm: number }) {
  const img = useImage(uri);
  const wpx = photo.width_px ?? 1;
  const k = W / wpx;
  const H = ((photo.height_px ?? wpx) * W) / wpx;
  const dash = { cut: null, fold: [8, 6], stitch: [2, 4], reference: null } as const;
  return (
    <View testID="photo-overlay">
      <Text variant="heading">{tm("make.cut.overlayHeading")}</Text>
      <View accessible accessibilityRole="image" accessibilityLabel={tm("make.cut.overlayAlt")}>
        <Canvas style={{ width: W, height: H }}>
          {img ? <SkImage image={img} x={0} y={0} width={W} height={H} fit="contain" /> : null}
          {plan.pieces.flatMap((p) =>
            p.lines.map((l) => {
              const svg = l.points_mm
                .map((pt, i) => {
                  const x = (projection.originPx[0] + pt[0] * projection.scalePxPerMm) * k;
                  const y = (projection.originPx[1] + pt[1] * projection.scalePxPerMm) * k;
                  return `${i === 0 ? "M" : "L"}${x} ${y}`;
                })
                .join(" ");
              const path = Skia.Path.MakeFromSVGString(svg);
              if (!path) return null;
              const d = dash[l.kind];
              return (
                <Path key={`${p.piece_id}-${l.line_id}`} path={path} style="stroke" strokeWidth={l.kind === "reference" ? 1 : 3} color="#d4145a">
                  {d ? <DashPathEffect intervals={[...d]} /> : null}
                </Path>
              );
            }),
          )}
        </Canvas>
      </View>
      <Text tone="secondary">{tm("make.cut.overlayApprox", { tol: mmToCmText(toleranceMm) })}</Text>
    </View>
  );
}
