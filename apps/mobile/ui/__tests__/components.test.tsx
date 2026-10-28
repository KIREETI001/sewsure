/**
 * Runs in apps/mobile with jest-expo and @testing-library/react-native v14,
 * where render, fireEvent and queries are async.
 */
import React from "react";
import { Text } from "react-native";
import { fireEvent, render, screen } from "@testing-library/react-native";
import {
  Button,
  Card,
  ChecklistItem,
  MeasurementInput,
  MockBadge,
  StateBadge,
  StepCard,
  ThemeProvider,
  minTouchTarget,
  parseCmToMm,
  uiStrings,
  type DesignState,
} from "..";

const wrap = (ui: React.ReactElement) => render(<ThemeProvider scheme="light">{ui}</ThemeProvider>);

describe("Button", () => {
  it("is a labelled button and fires onPress", async () => {
    const onPress = jest.fn();
    await wrap(<Button label="Continue" onPress={onPress} />);
    await fireEvent.press(screen.getByRole("button", { name: "Continue" }));
    expect(onPress).toHaveBeenCalledTimes(1);
  });

  it("is not pressable and reports disabled/busy while loading", async () => {
    const onPress = jest.fn();
    await wrap(<Button label="Save" loading onPress={onPress} />);
    const button = screen.getByRole("button", { name: "Save" });
    expect(button.props.accessibilityState).toMatchObject({ disabled: true, busy: true });
    await fireEvent.press(button);
    expect(onPress).not.toHaveBeenCalled();
  });

  it("meets the minimum touch target", async () => {
    await wrap(<Button label="Go" />);
    const style = [screen.getByRole("button", { name: "Go" }).props.style].flat(2);
    const merged = Object.assign({}, ...style.filter(Boolean));
    expect(merged.minHeight).toBeGreaterThanOrEqual(minTouchTarget);
  });
});

describe("StateBadge", () => {
  it.each([
    ["PASS_SUPPORTED_CHECKS", uiStrings.stateVerified, "✓"],
    ["NEEDS_INPUT", uiStrings.stateNeedsInfo, "?"],
    ["IDEA_ONLY", uiStrings.stateInspiration, "✦"],
    ["FAILED_CHECKS", uiStrings.stateFailed, "✗"],
    ["SUPERSEDED", uiStrings.stateSuperseded, "↺"],
  ] as [DesignState, string, string][])(
    "%s shows text and a symbol",
    async (state, label, symbol) => {
      await wrap(<StateBadge state={state} />);
      expect(screen.getByText(label)).toBeTruthy();
      // The symbol is hidden from screen readers on purpose.
      expect(screen.getByText(symbol, { includeHiddenElements: true })).toBeTruthy();
      expect(screen.getByLabelText(`${uiStrings.stateAccessibilityPrefix}: ${label}`)).toBeTruthy();
    },
  );

  it("uses a different label for every state", () => {
    const labels = [
      uiStrings.stateVerified,
      uiStrings.stateNeedsInfo,
      uiStrings.stateInspiration,
      uiStrings.stateFailed,
      uiStrings.stateSuperseded,
    ];
    expect(new Set(labels).size).toBe(5);
  });

  it("never uses guarantee wording", () => {
    const all = [
      uiStrings.stateVerified,
      uiStrings.stateNeedsInfo,
      uiStrings.stateInspiration,
      uiStrings.stateFailed,
      uiStrings.stateSuperseded,
    ].join(" ");
    expect(all).not.toMatch(/guarantee|perfect fit|100%|safe to cut/i);
  });
});

describe("MockBadge", () => {
  it("is visible text with an explanatory accessibility label", async () => {
    await wrap(<MockBadge />);
    expect(screen.getByText(/MOCK DATA/)).toBeTruthy();
    expect(screen.getByLabelText(uiStrings.mockAccessibility)).toBeTruthy();
  });
});

describe("parseCmToMm", () => {
  it.each([
    ["50", { status: "ok", mm: 500 }],
    ["50.5", { status: "ok", mm: 505 }],
    ["50,5", { status: "ok", mm: 505 }],
    ["0.1", { status: "ok", mm: 1 }],
    ["", { status: "empty", mm: null }],
    ["  ", { status: "empty", mm: null }],
    ["abc", { status: "invalid", mm: null }],
    ["-3", { status: "invalid", mm: null }],
    ["0", { status: "invalid", mm: null }],
    [".5", { status: "invalid", mm: null }],
    ["1.2.3", { status: "invalid", mm: null }],
    ["60 cm", { status: "invalid", mm: null }],
  ])("%p -> %p", (input, expected) => {
    expect(parseCmToMm(input)).toEqual(expected);
  });
});

describe("MeasurementInput", () => {
  it("displays the typed centimetre text and labels the unit", async () => {
    await wrap(<MeasurementInput label="Waist" text="82.5" onChange={() => {}} />);
    expect(screen.getByLabelText("Waist, cm").props.value).toBe("82.5");
    expect(screen.getByText("cm")).toBeTruthy();
  });

  it("emits text, millimetres and status when the user types centimetres", async () => {
    const onChange = jest.fn();
    await wrap(<MeasurementInput label="Waist" text="" onChange={onChange} />);
    await fireEvent.changeText(screen.getByLabelText("Waist, cm"), "82,5");
    expect(onChange).toHaveBeenLastCalledWith({ text: "82,5", status: "ok", mm: 825 });
    await fireEvent.changeText(screen.getByLabelText("Waist, cm"), "x");
    expect(onChange).toHaveBeenLastCalledWith({ text: "x", status: "invalid", mm: null });
    await fireEvent.changeText(screen.getByLabelText("Waist, cm"), "");
    expect(onChange).toHaveBeenLastCalledWith({ text: "", status: "empty", mm: null });
  });

  it("passes TextInput props such as onBlur through", async () => {
    const onBlur = jest.fn();
    await wrap(<MeasurementInput label="Waist" text="60" onChange={() => {}} onBlur={onBlur} />);
    await fireEvent(screen.getByLabelText("Waist, cm"), "blur");
    expect(onBlur).toHaveBeenCalledTimes(1);
  });

  it("shows an error with a non-colour marker", async () => {
    await wrap(
      <MeasurementInput label="Waist" text="" onChange={() => {}} errorText="Enter a number" />,
    );
    expect(screen.getByText("! Enter a number")).toBeTruthy();
  });
});

describe("ChecklistItem", () => {
  it("exposes checkbox role and checked state, and toggles", async () => {
    const onToggle = jest.fn();
    await wrap(<ChecklistItem label="Pre-wash fabric" checked={false} onToggle={onToggle} />);
    const item = screen.getByRole("checkbox", { name: "Pre-wash fabric" });
    expect(item.props.accessibilityState).toMatchObject({ checked: false });
    await fireEvent.press(item);
    expect(onToggle).toHaveBeenCalledWith(true);
  });

  it("shows a tick symbol when checked", async () => {
    await wrap(<ChecklistItem label="Pre-wash fabric" checked onToggle={() => {}} />);
    expect(screen.getByText("✓", { includeHiddenElements: true })).toBeTruthy();
  });
});

describe("StepCard", () => {
  it("announces step number, title and status, with a symbol for status", async () => {
    await wrap(
      <StepCard stepNumber={2} totalSteps={5} title="Mark the cut line" body="Use chalk." done />,
    );
    expect(
      screen.getByLabelText(/Step 2 of 5\. Mark the cut line\. Done\. Use chalk\./),
    ).toBeTruthy();
    expect(screen.getByText("✓ Done")).toBeTruthy();
  });

  it("marks not-done steps with text and a symbol", async () => {
    await wrap(<StepCard stepNumber={1} totalSteps={5} title="Prepare" body="Lay flat." />);
    expect(screen.getByText("○ Not done")).toBeTruthy();
  });
});

describe("Card", () => {
  it("renders children", async () => {
    await wrap(
      <Card>
        <Text>inside</Text>
      </Card>,
    );
    expect(screen.getByText("inside")).toBeTruthy();
  });
});
