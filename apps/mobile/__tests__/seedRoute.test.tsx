import { act, cleanup, fireEvent, render, screen } from "@testing-library/react-native";
import { useLocalSearchParams } from "expo-router";
import SeedRoute, { parseSeedName } from "@/dev/SeedRoute";
import { createIntakeSeed, INTAKE_SEED_NAMES } from "@/dev/intakeSeeds";
import { useIntakeStore } from "@/state/intakeStore";
import { getApi, mockApi, setApi } from "@/api/client";

jest.mock("expo-router", () => ({ useLocalSearchParams: jest.fn() }));
jest.mock("../app/(intake)/capture", () => () => null);
jest.mock("../app/(intake)/inspiration", () => () => null);
jest.mock("../app/(intake)/measurements", () => () => null);
const params = jest.mocked(useLocalSearchParams);
const originalPatch = useIntakeStore.getState().patch;

beforeEach(async () => {
  setApi(mockApi);
  await useIntakeStore.persist.rehydrate();
  useIntakeStore.getState().reset();
});
afterEach(async () => {
  await cleanup();
  jest.restoreAllMocks();
  useIntakeStore.setState({ patch: originalPatch });
  useIntakeStore.getState().reset();
  setApi(mockApi);
});

// First native Button render loads React Native modules; allow cold Windows CI startup.
it("offers mock-only failure controls without reseeding and cleans up on leaving", async () => {
  params.mockReturnValue({ name: "measurements-confirmed" });
  const view = await render(<SeedRoute />);
  const before = useIntakeStore.getState();
  await fireEvent.press(screen.getByRole("button", { name: "Enable mock upload failure" }));
  expect(screen.getByText("Mock upload failure: enabled")).toBeTruthy();
  expect(getApi()).not.toBe(mockApi);
  expect(useIntakeStore.getState()).toBe(before);
  await fireEvent.press(screen.getByRole("button", { name: "Disable mock upload failure" }));
  expect(getApi()).toBe(mockApi);
  await fireEvent.press(screen.getByRole("button", { name: "Enable mock upload failure" }));
  await view.unmount();
  expect(getApi()).toBe(mockApi);
}, 20000);

it.each(INTAKE_SEED_NAMES)(
  "applies %s once and displays the exact Maestro confirmation",
  async (name) => {
    params.mockReturnValue({ name });
    useIntakeStore.getState().patch({ extraMaterials: "stale synthetic scraps" });
    const patch = jest.spyOn(useIntakeStore.getState(), "patch");
    const view = await render(<SeedRoute />);
    expect(screen.getByText(`Seeded: ${name}`)).toBeTruthy();
    expect(useIntakeStore.getState()).toMatchObject(createIntakeSeed(name));
    expect(patch).toHaveBeenCalledTimes(1);
    await act(() => useIntakeStore.getState().patch({ extraMaterials: "new synthetic scraps" }));
    await view.rerender(<SeedRoute />);
    expect(patch).toHaveBeenCalledTimes(2);
    expect(useIntakeStore.getState().extraMaterials).toBe("new synthetic scraps");
  },
);

it.each([
  undefined,
  "",
  "unknown",
  "../capture-ready",
  ["capture-ready"],
  ["capture-ready", "inspiration-ready"],
])("rejects invalid or ambiguous parameters: %j", async (name) => {
  expect(parseSeedName(name)).toBeNull();
  params.mockReturnValue({ name } as ReturnType<typeof useLocalSearchParams>);
  const before = useIntakeStore.getState();
  await render(<SeedRoute />);
  expect(screen.getByText("Invalid seed name")).toBeTruthy();
  expect(useIntakeStore.getState()).toBe(before);
});

it("waits for hydration, then replaces stale persisted data exactly once", async () => {
  params.mockReturnValue({ name: "measurements-confirmed" });
  jest.spyOn(useIntakeStore.persist, "hasHydrated").mockReturnValue(false);
  let finish: (() => void) | undefined;
  const unsubscribe = jest.fn();
  jest.spyOn(useIntakeStore.persist, "onFinishHydration").mockImplementation((callback) => {
    finish = () => callback(useIntakeStore.getState());
    return unsubscribe;
  });
  const patch = jest.spyOn(useIntakeStore.getState(), "patch");
  const view = await render(<SeedRoute />);
  expect(screen.getByText("Waiting for intake hydration")).toBeTruthy();
  expect(patch).not.toHaveBeenCalled();
  // Simulate old persisted state arriving before hydration completes.
  await act(() => useIntakeStore.setState({ extraMaterials: "stale", category: "dress" }));
  await act(() => finish!());
  await act(() => finish!());
  expect(patch).toHaveBeenCalledTimes(1);
  expect(useIntakeStore.getState()).toMatchObject(createIntakeSeed("measurements-confirmed"));
  expect(screen.getByText("Seeded: measurements-confirmed")).toBeTruthy();
  await view.unmount();
  expect(unsubscribe).toHaveBeenCalledTimes(1);
});

it("unsubscribes if left before hydration and applies a new link independently", async () => {
  params.mockReturnValue({ name: "capture-ready" });
  const view = await render(<SeedRoute />);
  params.mockReturnValue({ name: "inspiration-ready" });
  await view.rerender(<SeedRoute />);
  expect(useIntakeStore.getState()).toMatchObject(createIntakeSeed("inspiration-ready"));
  expect(screen.getByText("Seeded: inspiration-ready")).toBeTruthy();
  jest.spyOn(useIntakeStore.persist, "hasHydrated").mockReturnValue(false);
  const unsubscribe = jest.fn();
  jest.spyOn(useIntakeStore.persist, "onFinishHydration").mockReturnValue(unsubscribe);
  params.mockReturnValue({ name: "measurements-confirmed" });
  await view.rerender(<SeedRoute />);
  await view.unmount();
  expect(unsubscribe).toHaveBeenCalledTimes(1);
});
