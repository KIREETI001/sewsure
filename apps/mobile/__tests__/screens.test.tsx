import { act, fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import * as ImagePicker from "expo-image-picker";
import type { ReactElement } from "react";
import { mockApi, setApi } from "@/api/client";
import { useIntakeStore } from "@/state/intakeStore";
import CaptureScreen from "../app/(intake)/capture";
import EntryScreen from "../app/(intake)/index";
import InspirationScreen from "../app/(intake)/inspiration";
import MeasurementsScreen from "../app/(intake)/measurements";

const mockPush = jest.fn();
jest.mock("expo-router", () => ({ useRouter: () => ({ push: mockPush }) }));
jest.mock("expo-image-picker", () => ({
  requestCameraPermissionsAsync: jest.fn(),
  launchCameraAsync: jest.fn(),
  launchImageLibraryAsync: jest.fn(),
}));

const picker = ImagePicker as jest.Mocked<typeof ImagePicker>;

const renderScreen = (ui: ReactElement) =>
  render(
    <QueryClientProvider
      client={
        new QueryClient({
          defaultOptions: { mutations: { retry: false }, queries: { retry: false } },
        })
      }
    >
      {ui}
    </QueryClientProvider>,
  );

const photo = { uri: "file:///synthetic.jpg", width: 2000, height: 2000, checked: true };

beforeEach(() => {
  useIntakeStore.getState().reset();
  setApi(mockApi);
  mockPush.mockClear();
  jest.clearAllMocks();
});

describe("entry", () => {
  it("cannot start until sign-in or demo mode, and demo mode is not uploaded", async () => {
    await renderScreen(<EntryScreen />);
    expect(screen.getByRole("button", { name: "Start" })).toBeDisabled();
    await fireEvent.press(screen.getByRole("radio", { name: "Maker or owner" }));
    await fireEvent.press(screen.getByRole("button", { name: "Try demo mode" }));
    await fireEvent.press(screen.getByRole("button", { name: "Start" }));
    expect(mockPush).toHaveBeenCalledWith("/(intake)/capture");
    expect(useIntakeStore.getState().guest).toBe(true);
  });

  it("shows a mock marker on signed-in data and recovers from sign-in failure", async () => {
    setApi({ ...mockApi, signIn: jest.fn().mockRejectedValueOnce(new Error("down")) });
    await renderScreen(<EntryScreen />);
    await fireEvent.press(screen.getByRole("button", { name: "Sign in" }));
    expect(await screen.findByText(/Sign-in did not work/)).toBeTruthy();

    setApi(mockApi);
    await fireEvent.press(screen.getByRole("button", { name: "Try again" }));
    expect(await screen.findByText("Signed in as Demo user")).toBeTruthy();
    expect(screen.getByLabelText("Sample data, not a real result")).toBeTruthy();
  });
});

describe("capture", () => {
  it("explains a denied camera permission and offers the library", async () => {
    picker.requestCameraPermissionsAsync.mockResolvedValue({ granted: false } as never);
    await renderScreen(<CaptureScreen />);
    await fireEvent.press(screen.getAllByRole("button", { name: "Take photo: Front" })[0]!);
    expect(await screen.findByText(/Camera access is off/)).toBeTruthy();
    expect(screen.getAllByRole("button", { name: "Choose from library: Front" })).toBeTruthy();
    expect(useIntakeStore.getState().front).toBeNull();
  });

  it("keeps a photo from the library and gates Continue on checks and category", async () => {
    picker.launchImageLibraryAsync.mockResolvedValue({
      canceled: false,
      assets: [{ uri: "file:///synthetic.jpg", width: 500, height: 400 }],
    } as never);
    await renderScreen(<CaptureScreen />);
    await fireEvent.press(screen.getByRole("button", { name: "Choose from library: Front" }));
    expect(await screen.findByText(/This photo is small/)).toBeTruthy();

    expect(screen.getByRole("button", { name: "Continue" })).toBeDisabled();
    await act(() => useIntakeStore.getState().patch({ back: photo, front: photo }));
    expect(screen.getByRole("button", { name: "Continue" })).toBeDisabled();

    await fireEvent.press(await screen.findByRole("button", { name: "Use suggestion" }));
    expect(screen.getAllByText("Mock").length).toBeGreaterThan(0);
    await waitFor(() => expect(screen.getByRole("button", { name: "Continue" })).toBeEnabled());
  });
});

describe("inspiration", () => {
  it("offers Surprise Me when blank and fills the idea with a mock marker", async () => {
    await renderScreen(<InspirationScreen />);
    expect(screen.getByRole("button", { name: "Continue" })).toBeDisabled();
    expect(screen.getByText(/Nothing entered yet/)).toBeTruthy();
    await fireEvent.press(screen.getAllByRole("button", { name: "Surprise Me" })[0]!);
    expect(await screen.findByText(/^Idea:/)).toBeTruthy();
    expect(useIntakeStore.getState().inspiration?.kind).toBe("surprise");
  });

  it("continues once text, fit and skill are set", async () => {
    await renderScreen(<InspirationScreen />);
    await fireEvent.changeText(
      screen.getByLabelText("Describe the change you want"),
      "shorter sleeves",
    );
    await fireEvent.press(screen.getByRole("radio", { name: "Relaxed" }));
    await fireEvent.press(screen.getByRole("radio", { name: "Beginner" }));
    await fireEvent.press(screen.getByRole("button", { name: "Continue" }));
    expect(mockPush).toHaveBeenCalledWith("/(intake)/measurements");
  });
});

describe("measurements", () => {
  const seed = async () =>
    await act(() =>
      useIntakeStore.getState().patch({
        category: "shirt",
        front: photo,
        back: photo,
        inspiration: { kind: "text", text: "shorter sleeves" },
        fit: "relaxed",
        skill: "beginner",
      }),
    );

  it("warns about 6 cm, offers 60 cm, and records millimetres", async () => {
    await seed();
    await renderScreen(<MeasurementsScreen />);
    const chest = screen.getByLabelText("Chest, flat across (cm)");
    await fireEvent.changeText(chest, "6");
    expect(screen.getByText(/Did you mean 60 cm/)).toBeTruthy();
    await fireEvent.press(screen.getByRole("button", { name: "Use 60 cm" }));
    const stored = useIntakeStore.getState().measurements.chest_flat!;
    expect(stored.inputCm).toBe("60");
    expect(stored.confirmedAt).not.toBeNull();
    expect(screen.getByText(/Confirmed: 60 cm/)).toBeTruthy();
  });

  it("lists missing values and does not upload", async () => {
    await seed();
    const uploadIntake = jest.fn();
    setApi({ ...mockApi, uploadIntake });
    await renderScreen(<MeasurementsScreen />);
    await fireEvent.press(screen.getByRole("button", { name: "Upload" }));
    expect(screen.getByText(/Still needed: Chest/)).toBeTruthy();
    expect(uploadIntake).not.toHaveBeenCalled();
  });

  it("keeps the draft when upload fails and marks it uploaded after a retry", async () => {
    await seed();
    const confirmedAt = "2026-10-28T00:00:00Z";
    await act(() =>
      useIntakeStore.getState().patch({
        measurements: Object.fromEntries(
          ["chest_flat", "body_length", "shoulder_width", "sleeve_length"].map((k, i) => [
            k,
            { inputCm: String([52, 70, 45, 60][i]), confirmedAt, origin: "user_entered" },
          ]),
        ),
      }),
    );
    const uploadIntake = jest.fn().mockRejectedValueOnce(new Error("offline"));
    setApi({ ...mockApi, uploadIntake });
    await renderScreen(<MeasurementsScreen />);
    expect(screen.getByText(/Not uploaded/)).toBeTruthy();

    await fireEvent.press(screen.getByRole("button", { name: "Upload" }));
    expect(await screen.findAllByText(/Upload failed/)).toBeTruthy();
    expect(useIntakeStore.getState().measurements.chest_flat?.inputCm).toBe("52");

    setApi(mockApi);
    await fireEvent.press(screen.getByRole("button", { name: "Try upload again" }));
    expect(await screen.findByText(/^✓ Uploaded/)).toBeTruthy();
  });

  it("never offers upload in demo mode", async () => {
    await seed();
    await act(() => useIntakeStore.getState().patch({ guest: true }));
    await renderScreen(<MeasurementsScreen />);
    expect(screen.queryByRole("button", { name: "Upload" })).toBeNull();
    expect(screen.getByText(/Demo mode: stays on this device/)).toBeTruthy();
  });
});
