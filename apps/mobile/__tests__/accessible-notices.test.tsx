import { act, fireEvent, render, screen } from "@testing-library/react-native";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Body, Notice } from "@/components/plain";
import { t } from "@/i18n";
import { useIntakeStore, type UploadStatus } from "@/state/intakeStore";
import MeasurementsScreen from "../app/(intake)/measurements";

describe("Notice accessibility", () => {
  it.each([
    ["warn", "!"],
    ["error", "✗"],
    ["info", "i"],
  ] as const)("hides only the decorative %s symbol", async (tone, symbol) => {
    await render(
      <Notice tone={tone}>
        <Body>Check this measurement.</Body>
      </Notice>,
    );

    // Preserve the existing container role without making it an accessible group.
    expect(screen.toJSON()).toMatchObject({ props: { accessibilityRole: "alert" } });
    expect(screen.getByText("Check this measurement.")).toBeVisible();
    expect(screen.queryByText(symbol)).toBeNull();
    const decoration = screen.getByText(symbol, { includeHiddenElements: true });
    expect(decoration).toHaveProp("accessible", false);
    expect(decoration).toHaveProp("accessibilityElementsHidden", true);
    expect(decoration).toHaveProp("importantForAccessibility", "no-hide-descendants");
    expect(decoration).toHaveTextContent(symbol);
  });
});

describe("measurement status accessibility", () => {
  beforeEach(() => useIntakeStore.getState().reset());

  const renderMeasurements = () =>
    render(
      <QueryClientProvider
        client={new QueryClient({ defaultOptions: { mutations: { retry: false, gcTime: Infinity } } })}
      >
        <MeasurementsScreen />
      </QueryClientProvider>,
    );

  it("speaks confirmation without its tick and keeps validation and edits working", async () => {
    await act(() => useIntakeStore.getState().patch({ category: "shirt" }));
    await renderMeasurements();
    const input = screen.getByLabelText("Chest, flat across (cm)");
    await fireEvent.changeText(input, "6");
    expect(screen.getByText(/Did you mean 60 cm/)).toBeVisible();
    expect(screen.queryByLabelText("Confirmed: 6 cm")).toBeNull();
    await fireEvent.press(screen.getByRole("button", { name: "Use 60 cm" }));
    expect(screen.getByLabelText("Confirmed: 60 cm")).toHaveTextContent("✓ Confirmed: 60 cm");
    expect(useIntakeStore.getState().measurements.chest_flat_width?.confirmedAt).not.toBeNull();
    await fireEvent.changeText(input, "52");
    expect(screen.queryByLabelText("Confirmed: 60 cm")).toBeNull();
    expect(useIntakeStore.getState().measurements.chest_flat_width?.confirmedAt).toBeNull();
    await fireEvent(input, "blur");
    expect(screen.getByLabelText("Confirmed: 52 cm")).toHaveTextContent("✓ Confirmed: 52 cm");
  });

  it.each<UploadStatus>(["not_uploaded", "uploading", "failed", "uploaded"])(
    "speaks the %s status without its decorative prefix",
    async (uploadStatus) => {
      await act(() => useIntakeStore.getState().patch({ uploadStatus }));
      await renderMeasurements();
      const messages = {
        not_uploaded: t("measure.draft.notUploaded"),
        uploading: t("measure.draft.uploading"),
        failed: t("measure.draft.failed"),
        uploaded: t("measure.draft.uploaded"),
      };
      const message = messages[uploadStatus];
      const prefix = uploadStatus === "uploaded" ? "✓" : "○";
      expect(screen.getByLabelText(message)).toHaveTextContent(`${prefix} ${message}`);
    },
  );

  it("retains the accessible mock qualifier beside the uploaded status", async () => {
    await act(() =>
      useIntakeStore.getState().patch({ uploadStatus: "uploaded", uploadProvenance: "mock" }),
    );
    await renderMeasurements();
    expect(screen.getByLabelText(t("measure.draft.uploaded"))).toHaveTextContent("✓ Uploaded");
    expect(screen.getByLabelText(t("common.mockHint"))).toBeVisible();
    expect(screen.getByText("Mock")).toBeVisible();
  });

  it("retains the demo draft message without speaking the circle", async () => {
    await act(() => useIntakeStore.getState().patch({ guest: true }));
    await renderMeasurements();
    const message = t("measure.draft.guest");
    expect(screen.getByLabelText(message)).toHaveTextContent(`○ ${message}`);
    expect(screen.queryByRole("button", { name: "Upload" })).toBeNull();
  });
});
