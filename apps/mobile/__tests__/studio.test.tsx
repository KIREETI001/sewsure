import { act, fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import fs from "fs";
import path from "path";
import type { ReactElement } from "react";
import { mockStudioApi, setMockScenario, setStudioApi, type StudioApi } from "@/api/studio";
import { useIntakeStore } from "@/state/intakeStore";
import { useStudioStore } from "@/state/studioStore";
import { cloneScenario, type ScenarioName } from "@/studio/scenarios";
import DesignScreen from "../app/(studio)/design";
import GeneratingScreen from "../app/(studio)/generating";
import ResultsScreen from "../app/(studio)/results";

const mockReplace = jest.fn();
const mockPush = jest.fn();
let mockParams: Record<string, string> = {};
jest.mock("expo-router", () => ({
  useRouter: () => ({ replace: mockReplace, push: mockPush, back: jest.fn() }),
  useLocalSearchParams: () => mockParams,
}));

const renderScreen = (ui: ReactElement) =>
  render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: Infinity } } })}
    >
      {ui}
    </QueryClientProvider>,
  );

const useScenario = async (name: ScenarioName) => {
  setMockScenario(name);
  useStudioStore.setState({ projectId: "p1", jobId: null });
  // Settle the mock job so results can read its outcome.
  const started = await mockStudioApi.generate("p1", { inspiration: { kind: "text", text: "x" } }, {
    idempotencyKey: `k-${name}`,
  });
  for (let i = 0; i < 6; i++) await mockStudioApi.getJob(started.data.job_id);
  useStudioStore.setState({ jobId: started.data.job_id });
};

beforeEach(() => {
  jest.clearAllMocks();
  mockParams = {};
  useStudioStore.getState().reset();
  useIntakeStore.getState().reset();
  setStudioApi(mockStudioApi);
  setMockScenario("woven_shirt_crop_pass");
});

describe("fixture copies", () => {
  it("match packages/contracts/fixtures byte for byte", () => {
    const src = path.resolve(__dirname, "../../../packages/contracts/fixtures");
    if (!fs.existsSync(src)) return;
    for (const f of fs.readdirSync(path.resolve(__dirname, "../src/studio/fixtures"))) {
      const a = JSON.parse(fs.readFileSync(path.resolve(__dirname, "../src/studio/fixtures", f), "utf8"));
      const b = JSON.parse(fs.readFileSync(path.join(src, f), "utf8"));
      expect(a).toEqual(b);
    }
  });
});

describe("generating", () => {
  beforeEach(() => jest.useFakeTimers());
  afterEach(() => jest.useRealTimers());

  it("progresses and then opens the results", async () => {
    await renderScreen(<GeneratingScreen />);
    expect(screen.getByText("Creating your redesigns")).toBeTruthy();
    await act(async () => {
      await jest.advanceTimersByTimeAsync(1500 * 6);
    });
    expect(mockReplace).toHaveBeenCalledWith("/results");
  });

  it("shows a model failure, keeps the request, and retry recovers", async () => {
    mockParams = { scenario: "job_failed_no_designs" };
    useIntakeStore.getState().patch({
      inspirationMode: "text",
      inspirationDraft: { imageUri: null, text: "shorter please", surprisePrompt: null },
    });
    await renderScreen(<GeneratingScreen />);
    await act(async () => {
      await jest.advanceTimersByTimeAsync(1500 * 6);
    });
    expect(screen.getByText(/took too long/)).toBeTruthy();
    expect(screen.getByText(/shorter please/)).toBeTruthy();
    expect(useIntakeStore.getState().inspirationDraft.text).toBe("shorter please");
    await fireEvent.press(screen.getByRole("button", { name: "Try again" }));
    await act(async () => {
      await jest.advanceTimersByTimeAsync(1500 * 6);
    });
    expect(mockReplace).toHaveBeenCalledWith("/results");
  });

  it("offers keep waiting or start again on timeout", async () => {
    mockParams = { scenario: "slow" };
    await renderScreen(<GeneratingScreen />);
    await act(async () => {
      await jest.advanceTimersByTimeAsync(95_000);
    });
    expect(screen.getByText("This is taking longer than usual")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Keep waiting" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Try again" })).toBeTruthy();
  });
});

describe("results", () => {
  it("shows two cards for two designs and does not pad", async () => {
    await useScenario("woven_shirt_crop_pass");
    await renderScreen(<ResultsScreen />);
    await waitFor(() => expect(screen.getByText("Showing 2 options")).toBeTruthy());
    expect(screen.getAllByRole("button", { name: /^View design/ })).toHaveLength(2);
    expect(screen.getAllByText(/MOCK DATA/).length).toBeGreaterThan(0);
  });

  it("shows one card with the binding constraint when none passed", async () => {
    await useScenario("lengthening_impossible");
    await renderScreen(<ResultsScreen />);
    await waitFor(() => expect(screen.getByText("Showing 1 option")).toBeTruthy());
    expect(screen.getByText("No option passed the checks")).toBeTruthy();
    expect(screen.getAllByText(/not long enough/).length).toBeGreaterThan(0);
    expect(screen.getByText(/15 cm short/)).toBeTruthy();
  });

  it("shows zero cards with the next step", async () => {
    await useScenario("zero_designs");
    await renderScreen(<ResultsScreen />);
    await waitFor(() => expect(screen.getByText("No option passed the checks")).toBeTruthy());
    expect(screen.queryAllByRole("button", { name: /^View design/ })).toHaveLength(0);
    expect(screen.getByRole("button", { name: "Change my request" })).toBeTruthy();
  });

  it("shows three cards for three designs", async () => {
    const base = cloneScenario("woven_shirt_crop_pass");
    const third = { ...base.designs.designs[1]!, design_id: "des-c", rank: 3, title: "Third" };
    const api: StudioApi = {
      ...mockStudioApi,
      listDesigns: async () => ({
        provenance: "mock",
        data: { ...base.designs, designs: [...base.designs.designs, third] },
      }),
    };
    setStudioApi(api);
    await renderScreen(<ResultsScreen />);
    await waitFor(() => expect(screen.getByText("Showing 3 options")).toBeTruthy());
  });

  it("shows a retry when the list fails", async () => {
    setStudioApi({
      ...mockStudioApi,
      listDesigns: async () => {
        throw new Error("offline");
      },
    });
    await renderScreen(<ResultsScreen />);
    await waitFor(() => expect(screen.getByText(/could not be loaded/)).toBeTruthy());
    expect(screen.getByRole("button", { name: "Try again" })).toBeTruthy();
  });
});

describe("design detail", () => {
  it("labels the outline approximate and shows numbers in cm", async () => {
    await useScenario("woven_shirt_crop_pass");
    mockParams = { designId: "des-crop-a" };
    await renderScreen(<DesignScreen />);
    await waitFor(() => expect(screen.getByText("Approximate outline")).toBeTruthy());
    expect(screen.getByText(/Approximate outline only/)).toBeTruthy();
    expect(screen.getByText("Original length: 78 cm")).toBeTruthy();
  });

  it("opens a superseded version read only", async () => {
    await useScenario("woven_shirt_crop_pass");
    mockParams = { designId: "des-crop-a", revisionId: "rev-crop-a-1" };
    await renderScreen(<DesignScreen />);
    await waitFor(() => expect(screen.getByText(/Read only: replaced/)).toBeTruthy());
    expect(screen.queryByRole("button", { name: "Recheck design" })).toBeNull();
  });

  it("an edit makes a new version and supersedes the old one", async () => {
    await useScenario("woven_shirt_crop_pass");
    mockParams = { designId: "des-crop-a" };
    await renderScreen(<DesignScreen />);
    const field = await screen.findByLabelText("Hem allowance, cm");
    await fireEvent.changeText(field, "3");
    await fireEvent.press(screen.getByRole("button", { name: "Recheck design" }));
    await waitFor(() => expect(screen.getByText(/Version 3 \(current\)/)).toBeTruthy());
    await fireEvent.press(screen.getByRole("button", { name: "Open version 2" }));
    await waitFor(() => expect(screen.getByText(/Read only: replaced/)).toBeTruthy());
  });

  it("keeps the edit when the recheck fails", async () => {
    await useScenario("woven_shirt_crop_pass");
    setStudioApi({
      ...mockStudioApi,
      createRevision: async () => {
        throw new Error("offline");
      },
    });
    mockParams = { designId: "des-crop-a" };
    await renderScreen(<DesignScreen />);
    const field = await screen.findByLabelText("Hem allowance, cm");
    await fireEvent.changeText(field, "3");
    await fireEvent.press(screen.getByRole("button", { name: "Recheck design" }));
    await waitFor(() => expect(screen.getByText(/recheck did not complete/)).toBeTruthy());
    expect(useStudioStore.getState().editDrafts["des-crop-a"]?.hem_allowance_mm).toBe("3");
  });

  it("offers no edits for an idea-only design", async () => {
    await useScenario("idea_only");
    mockParams = { designId: "des-idea-a" };
    await renderScreen(<DesignScreen />);
    await waitFor(() => expect(screen.getByText(/nothing you can change/)).toBeTruthy());
  });
});
