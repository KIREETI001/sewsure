import { fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactElement } from "react";
import { useMakeStore } from "../../src/make/store";
import CutScreen from "../../app/(make)/cut";
import DiyScreen from "../../app/(make)/diy";

let mockParams: Record<string, string> = {};
jest.mock("expo-router", () => ({
  useRouter: () => ({ push: jest.fn(), replace: jest.fn(), back: jest.fn() }),
  useLocalSearchParams: () => mockParams,
}));
jest.mock("@/make/components/PhotoOverlay", () => ({ PhotoOverlay: () => null }));

const wrap = async (ui: ReactElement) =>
  await render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: Infinity } } })}>{ui}</QueryClientProvider>,
  );

beforeEach(() => {
  mockParams = {};
  useMakeStore.setState({ byRevision: {}, hydrated: true });
});

describe("cut screen gate", () => {
  it.each(["rev-crop-a-1", "rev-idea-a-1", "rev-unsure-a-1", "rev-longer-a-1"])("%s shows a reason, no guide", async (id) => {
    mockParams = { revisionId: id };
    await wrap(<CutScreen />);
    await screen.findByTestId("gate-reason");
    expect(screen.queryByTestId("checkpoint-list")).toBeNull();
    expect(screen.queryByTestId("dimensioned-diagram")).toBeNull();
  });

  it("passing revision shows mock marker, draft banner, fallback and diagram", async () => {
    await wrap(<CutScreen />);
    await screen.findByTestId("dimensioned-diagram");
    expect(screen.getByTestId("draft-banner")).toBeTruthy();
    expect(screen.getByTestId("fallback-heading")).toBeTruthy();
    expect(screen.getByText(/MOCK DATA/)).toBeTruthy();
  });
});

describe("diy screen checkpoint enforcement", () => {
  it("cut step is locked until both checkpoints are ticked", async () => {
    await wrap(<DiyScreen />);
    await screen.findByTestId("progress-count");
    expect(screen.getByTestId("locked-s5_cut")).toBeTruthy();
    const cut = screen.getByLabelText(/I did this step: Cut along the line/);
    expect(cut.props.accessibilityState.disabled).toBe(true);
    // Checkpoint list is rendered inside the checkpoint step.
    const boxes = screen.getAllByRole("checkbox").filter((b) => /Measure straight|Repeat on the back/.test(b.props.accessibilityLabel));
    expect(boxes).toHaveLength(2);
    fireEvent.press(boxes[0]!);
    await waitFor(() => expect(screen.getByTestId("locked-s5_cut")).toBeTruthy());
    fireEvent.press(screen.getAllByRole("checkbox").filter((b) => /Repeat on the back/.test(b.props.accessibilityLabel))[0]!);
    await waitFor(() => expect(screen.queryByTestId("locked-s5_cut")).toBeNull());
  });

  it("resumes from stored progress", async () => {
    await wrap(<DiyScreen />);
    await waitFor(() => expect(screen.getByTestId("resume-banner")).toBeTruthy());
    expect(screen.getByTestId("resume-banner").props.children).toMatch(/step 3/i);
  });
});
