/**
 * D6 accessibility audit of the merged intake screens, run under Jest (not on a device).
 *
 * What this can show: every interactive element has a role and an accessible name, declared
 * minimum sizes in styles, text scaling is not disabled, and what text exists for disabled or
 * error states. What it cannot show: real layout at 200% font scale, TalkBack behaviour, or
 * actual touch-target pixels. See docs/qa/accessibility-checklist.md for what is verified how.
 *
 * Run from apps/mobile: npm run test:a11y
 * (`npx jest --testPathIgnorePatterns /node_modules/ --testMatch "**\/e2e/audit/*.test.tsx"`)
 *
 * All five former expected failures are ordinary regression tests after D2 integration.
 * Platform hiding props do not prove actual screen-reader speech.
 */
import { act, fireEvent, render, screen } from "@testing-library/react-native";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactElement } from "react";
import { StyleSheet, type StyleProp, type ViewStyle } from "react-native";
import { mockApi, setApi } from "@/api/client";
import { t, type MessageKey } from "@/i18n";
import { garmentSpecsFor } from "@/intake/measurements";
import { useIntakeStore } from "@/state/intakeStore";
import CaptureScreen from "../../app/(intake)/capture";
import EntryScreen from "../../app/(intake)/index";
import InspirationScreen from "../../app/(intake)/inspiration";
import MeasurementsScreen from "../../app/(intake)/measurements";

jest.mock("expo-router", () => ({ useRouter: () => ({ push: jest.fn() }) }));
jest.mock("expo-image-picker", () => ({
  requestCameraPermissionsAsync: jest.fn(),
  launchCameraAsync: jest.fn(),
  launchImageLibraryAsync: jest.fn(),
}));

const SYNTHETIC_PHOTO = { uri: "file:///synthetic.jpg", width: 2000, height: 2000, checked: true };

const renderScreen = async (ui: ReactElement) => {
  const view = await render(
    <QueryClientProvider
      client={
        new QueryClient({
          defaultOptions: {
            mutations: { retry: false, gcTime: Infinity },
            queries: { retry: false, gcTime: Infinity },
          },
        })
      }
    >
      {ui}
    </QueryClientProvider>,
  );
  // Wait for the real mock-query result so Capture updates settle inside async act.
  if (ui.type === CaptureScreen && useIntakeStore.getState().front !== null) {
    await screen.findByRole("button", { name: t("capture.category.use") });
  }
  return view;
};

beforeEach(() => {
  useIntakeStore.getState().reset();
  setApi(mockApi);
});

type Host = {
  type: string;
  props: Record<string, unknown>;
  children: unknown[];
};

const hosts = (): Host[] => {
  const out: Host[] = [];
  const walk = (n: unknown) => {
    if (!n || typeof n !== "object") return;
    const node = n as Host;
    out.push({ ...node, children: node.children ?? [] });
    for (const c of node.children ?? []) walk(c);
  };
  const json = screen.toJSON() as unknown;
  for (const r of Array.isArray(json) ? json : [json]) walk(r);
  return out;
};

const INTERACTIVE = ["button", "radio", "checkbox"];
const interactive = () =>
  hosts().filter((n) => INTERACTIVE.includes(n.props.accessibilityRole as string));

const textOf = (n: Host): string =>
  n.children
    .map((c) => (typeof c === "string" ? c : c && typeof c === "object" ? textOf(c as Host) : ""))
    .join("");

const nameOf = (n: Host): string => (n.props.accessibilityLabel as string) || textOf(n);

const sizeOf = (n: Host) => {
  const s = StyleSheet.flatten(n.props.style as StyleProp<ViewStyle>) ?? {};
  return {
    minHeight: Number(s.minHeight ?? s.height ?? 0),
    minWidth: Number(s.minWidth ?? s.width ?? 0),
  };
};

const duplicates = (names: string[]) => [
  ...new Set(names.filter((x, i) => names.indexOf(x) !== i)),
];

const seedReady = () =>
  act(() =>
    useIntakeStore.getState().patch({
      category: "shirt",
      front: SYNTHETIC_PHOTO,
      back: SYNTHETIC_PHOTO,
      inspirationMode: "text",
      inspirationDraft: { imageUri: null, text: "shorter sleeves", surprisePrompt: null },
      fit: "relaxed",
      skill: "beginner",
    }),
  );

const screens: [string, () => Promise<unknown>, ReactElement][] = [
  ["entry", async () => {}, <EntryScreen key="e" />],
  ["capture (empty)", async () => {}, <CaptureScreen key="c0" />],
  [
    "capture (both photos)",
    async () =>
      act(() => useIntakeStore.getState().patch({ front: SYNTHETIC_PHOTO, back: SYNTHETIC_PHOTO })),
    <CaptureScreen key="c1" />,
  ],
  ["inspiration", async () => {}, <InspirationScreen key="i" />],
  ["measurements", seedReady, <MeasurementsScreen key="m" />],
];

describe.each(screens)("%s", (_name, prepare, element) => {
  beforeEach(async () => {
    await prepare();
    await renderScreen(element);
  });

  it("gives every interactive element a role and a non-empty accessible name", () => {
    expect(interactive().filter((n) => nameOf(n).trim() === "")).toHaveLength(0);
  });

  it("declares at least 44 pt minimum size on every interactive element", () => {
    const small = interactive()
      .map((n) => ({ name: nameOf(n), ...sizeOf(n) }))
      .filter((s) => s.minHeight < 44 || s.minWidth < 44);
    expect(small).toEqual([]);
  });

  it("does not switch off text scaling or cap it below 200%", () => {
    const offenders = hosts().filter(
      (n) =>
        n.props.allowFontScaling === false ||
        (typeof n.props.maxFontSizeMultiplier === "number" && n.props.maxFontSizeMultiplier < 2),
    );
    expect(offenders).toHaveLength(0);
  });

  it("has no fixed height on text or text inputs (clipping risk at 200%)", () => {
    const fixed = hosts().filter((n) => {
      if (n.type !== "Text" && n.type !== "TextInput") return false;
      const s = StyleSheet.flatten(n.props.style as StyleProp<ViewStyle>) ?? {};
      return typeof s.height === "number";
    });
    expect(fixed).toHaveLength(0);
  });
});

describe("duplicate accessible names (a screen-reader user cannot tell them apart)", () => {
  it("capture with both photos: Retake and photo checks have distinct side-specific names", async () => {
    await act(() =>
      useIntakeStore.getState().patch({ front: SYNTHETIC_PHOTO, back: SYNTHETIC_PHOTO }),
    );
    await renderScreen(<CaptureScreen />);
    expect(duplicates(interactive().map(nameOf))).toEqual([]);
    for (const side of ["Front", "Back"]) {
      expect(screen.getByRole("button", { name: `Retake: ${side}` })).toBeVisible();
      expect(
        screen.getByRole("checkbox", { name: `${t("capture.check.all")}: ${side}` }),
      ).toBeChecked();
    }
  });
});

describe("disabled and blocked states say why, in text", () => {
  it("entry: Start is disabled and the screen explains what is needed", async () => {
    await renderScreen(<EntryScreen />);
    expect(screen.getByRole("button", { name: "Start" })).toBeDisabled();
    expect(screen.getByText(t("entry.startNeedsMaker"))).toBeVisible();
    expect(screen.getByText(t("entry.startNeedsSession"))).toBeVisible();
    await fireEvent.press(screen.getByRole("radio", { name: "Maker or owner" }));
    expect(screen.queryByText(t("entry.startNeedsMaker"))).toBeNull();
    expect(screen.getByText(t("entry.startNeedsSession"))).toBeVisible();
    expect(screen.getByRole("button", { name: "Start" })).toBeDisabled();
    await fireEvent.press(screen.getByRole("button", { name: "Try demo mode" }));
    expect(screen.queryByText(t("entry.startNeedsSession"))).toBeNull();
    expect(screen.getByRole("button", { name: "Start" })).toBeEnabled();
  });

  it("inspiration: Continue is disabled with only fit and skill missing; screen explains", async () => {
    await act(() =>
      useIntakeStore.getState().patch({
        inspirationMode: "text",
        inspirationDraft: { imageUri: null, text: "shorter sleeves", surprisePrompt: null },
      }),
    );
    await renderScreen(<InspirationScreen />);
    expect(screen.getByRole("button", { name: "Continue" })).toBeDisabled();
    expect(screen.getByText(t("inspiration.fit.needed"))).toBeVisible();
    expect(screen.getByText(t("inspiration.skill.needed"))).toBeVisible();
    await fireEvent.press(screen.getByRole("radio", { name: "Relaxed" }));
    expect(screen.queryByText(t("inspiration.fit.needed"))).toBeNull();
    expect(screen.getByText(t("inspiration.skill.needed"))).toBeVisible();
    expect(screen.getByRole("button", { name: "Continue" })).toBeDisabled();
    await fireEvent.press(screen.getByRole("radio", { name: "Beginner" }));
    expect(screen.queryByText(t("inspiration.skill.needed"))).toBeNull();
    expect(screen.getByRole("button", { name: "Continue" })).toBeEnabled();
  });
});

describe("input format hint", () => {
  it("measurements: the cm format hint is visible text, not only a screen-reader hint", async () => {
    await seedReady();
    await renderScreen(<MeasurementsScreen />);
    const specs = garmentSpecsFor("shirt");
    const hints = screen.getAllByText(t("measure.hint"));
    expect(hints).toHaveLength(specs.length);
    for (const hint of hints) expect(hint).toBeVisible();
    for (const spec of specs) {
      const label = `${t(`measure.field.${spec.key}` as MessageKey)} (cm)`;
      expect(screen.getByLabelText(label)).toHaveProp("accessibilityHint", t("measure.hint"));
    }
  });
});

describe("states do not rely on colour alone", () => {
  it("measurements: an implausible value shows text and a symbol", async () => {
    await seedReady();
    await renderScreen(<MeasurementsScreen />);
    await fireEvent.changeText(screen.getByLabelText("Chest, flat across (cm)"), "6");
    expect(screen.getByText(/looks small. Did you mean 60 cm/)).toBeTruthy();
    const alert = hosts().find((n) => n.props.accessibilityRole === "alert");
    expect(alert).toBeDefined();
    expect(textOf(alert as Host)).toMatch(/^[!✗i]/);
  });

  it("selected chips carry a tick symbol and a checked state", async () => {
    await renderScreen(<InspirationScreen />);
    await fireEvent.press(screen.getByRole("radio", { name: "Relaxed" }));
    const chip = screen.getByRole("radio", { name: "Relaxed" });
    expect(chip).toBeChecked();
    expect(textOf(chip as unknown as Host)).toContain("✓");
  });
});

describe("decorative symbols are hidden from the screen reader", () => {
  it("notice symbols (!, ✗, i) expose platform hiding props while message stays visible", async () => {
    await seedReady();
    await renderScreen(<MeasurementsScreen />);
    await fireEvent.changeText(screen.getByLabelText("Chest, flat across (cm)"), "6");
    expect(screen.getByText("6 cm looks small. Did you mean 60 cm?")).toBeVisible();
    const symbols = hosts().filter((n) => n.type === "Text" && /^[!✗i]\s*$/.test(textOf(n)));
    expect(symbols.length).toBeGreaterThan(0);
    for (const s of symbols) {
      expect(s.props.accessible).toBe(false);
      expect(s.props.accessibilityElementsHidden).toBe(true);
      expect(s.props.importantForAccessibility).toBe("no-hide-descendants");
    }
  });
});
