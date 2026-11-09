import { lineDepthMm, lineDepthRangeMm, mmToCmText, mmToInchText, planBounds } from "../../src/make/geometry";
import { lineText } from "../../src/make/components/DimensionedDiagram";
import crop from "../../../../packages/contracts/fixtures/woven_shirt_crop_pass.json";
import type { CutLine, CutPlan } from "../../src/make/types";

const line = (pts: [number, number][], kind: CutLine["kind"] = "cut"): CutLine =>
  ({ line_id: "l", kind, label: "Cut 525 mm below shoulder", points_mm: pts }) as unknown as CutLine;
const plan = crop.cut_plan as unknown as CutPlan;

describe("mm to cm and inches", () => {
  it.each([
    [525, "52.5", "20 5/8"],
    [500, "50", "19 5/8"],
    [3, "0.3", "1/8"],
    [0, "0", "0"],
    [254, "25.4", "10"],
  ])("%s mm", (mm, cm, inch) => {
    expect(mmToCmText(mm)).toBe(cm);
    expect(mmToInchText(mm)).toBe(inch);
  });
});

describe("lineDepthMm", () => {
  it("gives the depth of a level line", () => {
    expect(lineDepthMm(line([[0, 525], [280, 525]]))).toBe(525);
  });
  it("is null for a curved hem and for a vertical line", () => {
    expect(lineDepthMm(line([[0, 500], [140, 540], [280, 500]]))).toBeNull();
    expect(lineDepthMm(line([[0, 0], [0, 500]]))).toBeNull();
  });
  it("reports the true range for those lines", () => {
    expect(lineDepthRangeMm(line([[0, 500], [140, 540], [280, 500]]))).toEqual([500, 540]);
  });
});

describe("lineText", () => {
  it("uses the kind and cm, not the fixture label's millimetres", () => {
    const t = lineText(line([[0, 525], [280, 525]]), plan);
    expect(t).toContain("52.5 cm");
    expect(t).not.toMatch(/\bmm\b/);
  });
  it("gives a range for a curved line, never the 51.3 cm mean of a 54 cm deep curve", () => {
    const t = lineText(line([[0, 500], [140, 540], [280, 500]]), plan);
    expect(t).toContain("between 50 cm and 54 cm");
    expect(t).not.toContain("51.3");
  });
  it("gives a range for a vertical line, never '25 cm below'", () => {
    const t = lineText(line([[0, 0], [0, 500]]), plan);
    expect(t).toContain("between 0 cm and 50 cm");
  });
});

describe("planBounds", () => {
  it("spans all points", () => {
    expect(planBounds([line([[0, 5], [10, 20]]), line([[-4, 9], [3, 1]])])).toEqual({
      minX: -4,
      minY: 1,
      maxX: 10,
      maxY: 20,
    });
  });
});
