import type { GarmentCategory, MeasurementGroup } from "@/api/types";

export interface MeasurementSpec {
  key: string;
  group: MeasurementGroup;
  /** Typical range in mm. Outside it we warn but let the user keep the value. */
  typicalMm: readonly [number, number];
  /** Hard range in mm. Outside it the value is rejected. */
  hardMm: readonly [number, number];
}

const spec = (
  key: string,
  group: MeasurementGroup,
  typicalMm: [number, number],
  hardMm: [number, number],
): MeasurementSpec => ({ key, group, typicalMm, hardMm });

const chestFlat = spec("chest_flat", "garment", [400, 700], [200, 900]);
const waistFlat = spec("waist_flat", "garment", [300, 600], [150, 800]);
const hipFlat = spec("hip_flat", "garment", [380, 700], [200, 900]);

const GARMENT_SPECS: Record<GarmentCategory, MeasurementSpec[]> = {
  shirt: [
    chestFlat,
    spec("body_length", "garment", [550, 850], [250, 1100]),
    spec("shoulder_width", "garment", [350, 550], [200, 700]),
    spec("sleeve_length", "garment", [150, 750], [50, 900]),
  ],
  tee: [
    chestFlat,
    spec("body_length", "garment", [550, 850], [250, 1100]),
    spec("shoulder_width", "garment", [350, 550], [200, 700]),
    spec("sleeve_length", "garment", [100, 300], [30, 900]),
  ],
  jacket: [
    chestFlat,
    spec("body_length", "garment", [500, 900], [250, 1200]),
    spec("shoulder_width", "garment", [380, 600], [200, 750]),
    spec("sleeve_length", "garment", [500, 750], [200, 900]),
  ],
  trousers: [
    waistFlat,
    hipFlat,
    spec("inseam", "garment", [600, 900], [200, 1100]),
    spec("rise", "garment", [200, 380], [100, 500]),
  ],
  skirt: [waistFlat, hipFlat, spec("skirt_length", "garment", [300, 900], [150, 1200])],
  dress: [chestFlat, waistFlat, hipFlat, spec("dress_length", "garment", [700, 1500], [300, 1800])],
};

/** Optional, reusable body profile. Never required to continue. */
export const BODY_SPECS: MeasurementSpec[] = [
  spec("height", "body", [1400, 2000], [800, 2300]),
  spec("bust", "body", [700, 1300], [400, 1800]),
  spec("waist", "body", [550, 1200], [350, 1700]),
  spec("hip", "body", [750, 1400], [450, 1800]),
];

export const garmentSpecsFor = (category: GarmentCategory): MeasurementSpec[] =>
  GARMENT_SPECS[category];
