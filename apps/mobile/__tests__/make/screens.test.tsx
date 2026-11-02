import { fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactElement } from "react";
import * as data from "../../src/make/data";
import { useMakeStore } from "../../src/make/store";
import CutScreen from "../../app/(make)/cut";
import DiyScreen from "../../app/(make)/diy";

let mockParams: Record<string, string | string[]> = {};
const mockBack = jest.fn();
const mockReplace = jest.fn();
let mockCanGoBack = true;
jest.mock("expo-router", () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: mockReplace,
    back: mockBack,
    canGoBack: () => mockCanGoBack,
  }),
  useLocalSearchParams: () => mockParams,
}));

const PASS = "rev-crop-a-2";
const newClient = () => new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: Infinity } } });
const wrap = async (ui: ReactElement, client = newClient()) =>
  await render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);

beforeEach(() => {
  mockParams = { revisionId: PASS };
  mockCanGoBack = true;
  mockBack.mockClear();
  mockReplace.mockClear();
  useMakeStore.setState({ byRevision: {}, hydrated: true });
});
afterEach(() => jest.restoreAllMocks());

const tickCheckpoints = async () => {
  for (const re of [/Measure straight down/, /Repeat on the back/]) {
    const box = screen.getAllByRole("checkbox").filter((b) => re.test(b.props.accessibilityLabel))[0]!;
    if (box.props.accessibilityState.checked !== true) await fireEvent.press(box);
  }
};

const tickEarlier = async () => {
  const box = screen.getByLabelText(/I did this step: Mark the cut line/);
  if (box.props.accessibilityState.checked !== true) await fireEvent.press(box);
};

describe("state gate on both screens, with a plan and steps present", () => {
  it.each(["IDEA_ONLY", "NEEDS_INPUT", "FAILED_CHECKS", "SUPERSEDED"])(
    "%s never renders the guide, even when the bundle carries a plan and steps",
    async (status) => {
      const real = await data.loadMakeBundle(PASS);
      const bundle = { ...real!, revision: { ...real!.revision, status } } as never;
      expect(real!.cutPlan).toBeTruthy();
      expect(real!.diySteps).toBeTruthy();
      jest.spyOn(data, "loadMakeBundle").mockResolvedValue(bundle);

      const cut = await wrap(<CutScreen />);
      await screen.findByTestId("gate-reason");
      expect(screen.queryByTestId("checkpoint-list")).toBeNull();
      expect(screen.queryByTestId("dimensioned-diagram")).toBeNull();
      await cut.unmount();

      await wrap(<DiyScreen />);
      await screen.findByTestId("gate-reason");
      expect(screen.queryByTestId("progress-count")).toBeNull();
      expect(screen.queryByTestId("checkpoint-list")).toBeNull();
      expect(screen.queryByText(/Cut through one layer/)).toBeNull();
    },
  );
});

describe("cut screen gate", () => {
  it.each(["rev-crop-a-1", "rev-idea-a-1", "rev-unsure-a-1", "rev-longer-a-1"])("%s shows a reason, no guide", async (id) => {
    mockParams = { revisionId: id };
    await wrap(<CutScreen />);
    await screen.findByTestId("gate-reason");
    expect(screen.queryByTestId("checkpoint-list")).toBeNull();
    expect(screen.queryByTestId("dimensioned-diagram")).toBeNull();
  });

  it.each([
    ["missing", {}],
    ["empty", { revisionId: "" }],
    ["array", { revisionId: [PASS, "x"] }],
    ["wrong param name", { designId: "des-idea-a" }],
  ])("fails closed with a %s revisionId: never opens a passing guide", async (_n, params) => {
    mockParams = params as Record<string, string | string[]>;
    await wrap(<CutScreen />);
    await screen.findByTestId("gate-reason");
    expect(screen.queryByTestId("dimensioned-diagram")).toBeNull();
    expect(screen.queryByTestId("checkpoint-list")).toBeNull();
  });

  it("an unknown revision is a closed gate, not an endless retry", async () => {
    mockParams = { revisionId: "rev-from-the-studio-edit" };
    await wrap(<CutScreen />);
    await screen.findByTestId("gate-reason");
    expect(screen.queryByText(/did not load/)).toBeNull();
    expect(screen.queryByTestId("dimensioned-diagram")).toBeNull();
  });

  it("passing revision shows demo marker, draft banner, fallback and diagram, with no green verified badge", async () => {
    await wrap(<CutScreen />);
    await screen.findByTestId("dimensioned-diagram");
    expect(screen.getByTestId("draft-banner")).toBeTruthy();
    expect(screen.getByTestId("demo-badge")).toBeTruthy();
    expect(screen.getByTestId("fallback-heading")).toBeTruthy();
    expect(screen.getByText(/MOCK DATA/)).toBeTruthy();
    expect(screen.queryByText(/Verified within supported checks/)).toBeNull();
  });

  it("does not show a cached passing guide while a refetch runs", async () => {
    const client = newClient();
    const real = await data.loadMakeBundle(PASS);
    client.setQueryData(["make", PASS], real);
    jest.spyOn(data, "loadMakeBundle").mockReturnValue(new Promise(() => {}));
    await wrap(<CutScreen />, client);
    expect(screen.queryByTestId("dimensioned-diagram")).toBeNull();
    expect(screen.queryByTestId("checkpoint-list")).toBeNull();
  });

  it("back falls back to the start screen after a deep link with no history", async () => {
    mockParams = { revisionId: "rev-idea-a-1" };
    mockCanGoBack = false;
    await wrap(<CutScreen />);
    await fireEvent.press(await screen.findByText("Back"));
    expect(mockBack).not.toHaveBeenCalled();
    expect(mockReplace).toHaveBeenCalledWith("/");
  });
});

describe("diy screen gate", () => {
  it("N9: does not show a cached passing guide while a refetch runs", async () => {
    const client = newClient();
    client.setQueryData(["make", PASS], await data.loadMakeBundle(PASS));
    jest.spyOn(data, "loadMakeBundle").mockReturnValue(new Promise(() => {}));
    await wrap(<DiyScreen />, client);
    expect(screen.queryByTestId("progress-count")).toBeNull();
    expect(screen.queryByTestId("checkpoint-list")).toBeNull();
  });

  it.each([[{}], [{ revisionId: [PASS] }]])("fails closed without a single revisionId", async (params) => {
    mockParams = params as Record<string, string | string[]>;
    await wrap(<DiyScreen />);
    await screen.findByTestId("gate-reason");
    expect(screen.queryByTestId("progress-count")).toBeNull();
  });
});

const stepCard = (n: number) => screen.getByLabelText(new RegExp(`^Step ${n} of 7`));

describe("diy screen checkpoint enforcement", () => {
  it("hides the cut instruction while locked, and shows it once the checkpoints are ticked", async () => {
    await wrap(<DiyScreen />);
    await screen.findByTestId("progress-count");
    expect(screen.queryByText(/Cut through one layer/)).toBeNull();
    expect(stepCard(5).props.accessibilityLabel).not.toMatch(/Cut through one layer/);
    expect(screen.getByText(/Locked\. Finish the earlier steps first\./)).toBeTruthy();
    const cutTick = screen.getByLabelText(/I did this step: Cut along the line/);
    expect(cutTick.props.accessibilityState.disabled).toBe(true);

    await tickEarlier();
    expect(screen.getByText(/Locked\. Tick every ruler checkpoint in step 4 first\./)).toBeTruthy();
    await tickCheckpoints();
    await waitFor(() => expect(screen.getByText(/Cut through one layer/)).toBeTruthy());
  });

  it("the checkpoint step has no tick of its own and is done only when every checkpoint is ticked", async () => {
    await wrap(<DiyScreen />);
    await screen.findByTestId("progress-count");
    expect(screen.queryByLabelText(/I did this step: Check the marks/)).toBeNull();
    expect(stepCard(4).props.accessibilityLabel).toMatch(/Not done/);
    await fireEvent.press(screen.getAllByRole("checkbox").filter((b) => /Measure straight down/.test(b.props.accessibilityLabel))[0]!);
    await waitFor(() => expect(stepCard(4).props.accessibilityLabel).toMatch(/Not done/));
    await tickEarlier();
    await tickCheckpoints();
    await waitFor(() => expect(stepCard(4).props.accessibilityLabel).toMatch(/\bDone\b/));
  });

  it("steps after the cut stay locked until the cut is ticked", async () => {
    await wrap(<DiyScreen />);
    await screen.findByTestId("progress-count");
    for (const title of ["Hem", "Measure the result"]) {
      const box = screen.getByLabelText(new RegExp(`I did this step: ${title}`));
      expect(box.props.accessibilityState.disabled).toBe(true);
      await fireEvent.press(box);
    }
    expect(screen.getAllByText(/Locked\. Finish the cut step first\./)).toHaveLength(2);
    expect(screen.getByTestId("progress-count").props.children).toMatch(/^2 of 7/);

    await tickEarlier();
    await tickCheckpoints();
    await waitFor(() =>
      expect(screen.getByLabelText(/I did this step: Cut along the line/).props.accessibilityState.disabled).toBe(false),
    );
    expect(screen.getByLabelText(/I did this step: Hem/).props.accessibilityState.disabled).toBe(true);
    await fireEvent.press(screen.getByLabelText(/I did this step: Cut along the line/));
    await waitFor(() =>
      expect(screen.getByLabelText(/I did this step: Hem/).props.accessibilityState.disabled).toBe(false),
    );
  });

  it("N2: ticked checkpoints do not unlock the cut while an earlier step is not done", async () => {
    await wrap(<DiyScreen />);
    await screen.findByTestId("progress-count");
    expect(screen.getByTestId("checkpoints-locked")).toBeTruthy();
    for (const re of [/Measure straight down/, /Repeat on the back/]) {
      const box = screen.getAllByRole("checkbox").filter((b) => re.test(b.props.accessibilityLabel))[0]!;
      expect(box.props.accessibilityState.disabled).toBe(true);
      await fireEvent.press(box);
    }
    expect(screen.getByLabelText(/I did this step: Cut along the line/).props.accessibilityState.disabled).toBe(true);
    expect(screen.queryByText(/Cut through one layer/)).toBeNull();
    await tickEarlier();
    await waitFor(() => expect(screen.queryByTestId("checkpoints-locked")).toBeNull());
  });

  it("N2: the cut screen shows checkpoints locked until the earlier steps are done", async () => {
    await wrap(<CutScreen />);
    await screen.findByTestId("checkpoint-list");
    expect(screen.getByTestId("checkpoints-locked")).toBeTruthy();
    const box = screen.getAllByRole("checkbox").find((b) => /Measure straight down/.test(b.props.accessibilityLabel))!;
    expect(box.props.accessibilityState.disabled).toBe(true);
  });

  it("N9: checkpoints and steps stored for a different cut plan do not count", async () => {
    const real = await data.loadMakeBundle(PASS);
    const ids = real!.cutPlan!.ruler_checkpoints.map((c) => c.checkpoint_id);
    useMakeStore.setState({
      byRevision: {
        [PASS]: {
          cutPlanId: "some-other-plan",
          checkpoints: Object.fromEntries(ids.map((i) => [i, true])),
          steps: { s1_prepare: true, s2_measure: true, s3_mark: true },
          updatedAt: "2026-01-01T00:00:00Z",
        },
      } as never,
      hydrated: true,
    });
    await wrap(<DiyScreen />);
    await screen.findByTestId("progress-count");
    expect(screen.queryByText(/Cut through one layer/)).toBeNull();
    expect(screen.getByLabelText(/I did this step: Cut along the line/).props.accessibilityState.disabled).toBe(true);
  });

  it("resumes from stored progress", async () => {
    await wrap(<DiyScreen />);
    await waitFor(() => expect(screen.getByTestId("resume-banner")).toBeTruthy());
    expect(screen.getByTestId("resume-banner").props.children).toMatch(/step 3/i);
  });

  it("a finished cut restored from the server shows done, not locked", async () => {
    const real = await data.loadMakeBundle(PASS);
    const done = (id: string) => ({ step_id: id, self_verification: "self_reported_done" });
    jest.spyOn(data, "loadMakeBundle").mockResolvedValue({
      ...real!,
      serverProgress: {
        ...real!.serverProgress!,
        steps: ["s1_prepare", "s2_measure", "s3_mark", "s5_cut"].map(done),
      } as never,
    });
    await wrap(<DiyScreen />);
    await waitFor(() => expect(stepCard(5).props.accessibilityLabel).toMatch(/\bDone\b/));
    expect(stepCard(4).props.accessibilityLabel).toMatch(/\bDone\b/);
    expect(screen.getByTestId("resume-banner").props.children).toMatch(/step 6/i);
  });
});

describe("diy screen accessibility and draft marking", () => {
  it("announces 'cannot be undone' and 'Locked' in the step's label, and the tick box is a reachable sibling", async () => {
    await wrap(<DiyScreen />);
    await screen.findByTestId("progress-count");
    const label: string = stepCard(5).props.accessibilityLabel;
    expect(label).toMatch(/cannot be undone/);
    expect(label).toMatch(/Locked/);
    // The tick box is not a child of the accessible card.
    const card = stepCard(5);
    const tick = screen.getByLabelText(/I did this step: Cut along the line/);
    const inside = (n: { parent: unknown }, target: unknown): boolean => {
      for (let p = n as { parent: unknown } | null; p; p = p.parent as { parent: unknown } | null) if (p === target) return true;
      return false;
    };
    expect(inside(tick as never, card)).toBe(false);
  });

  it("marks the irreversible step as demo-only, not just the page header", async () => {
    await wrap(<DiyScreen />);
    await screen.findByTestId("progress-count");
    expect(stepCard(5).props.accessibilityLabel).toMatch(/not yet reviewed/i);
  });

  it("checkpoint labels carry the distance for screen readers", async () => {
    await wrap(<CutScreen />);
    await screen.findByTestId("checkpoint-list");
    const box = screen.getAllByRole("checkbox").find((b) => /Measure straight down/.test(b.props.accessibilityLabel))!;
    expect(box.props.accessibilityLabel).toMatch(/52\.5 cm/);
  });
});
