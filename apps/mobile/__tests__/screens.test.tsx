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
          defaultOptions: {
            mutations: { retry: false },
            queries: { retry: false, gcTime: Infinity },
          },
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
  it("distinguishes Front and Back Retake buttons without changing their visible text", async () => {
    await act(() => useIntakeStore.getState().patch({ front: photo, back: photo }));
    await renderScreen(<CaptureScreen />);
    expect(screen.getByRole("button", { name: "Retake: Front" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Retake: Back" })).toBeTruthy();
    expect(screen.getAllByText("Retake")).toHaveLength(2);
  });

  it("distinguishes photo checks and toggles only the named side", async () => {
    await act(() =>
      useIntakeStore.getState().patch({
        front: { ...photo, checked: false },
        back: { ...photo, checked: false },
        category: "shirt",
      }),
    );
    await renderScreen(<CaptureScreen />);
    const checkLabel = "Sharp, evenly lit, and the whole garment is in frame";
    const frontCheck = screen.getByRole("checkbox", { name: `${checkLabel}: Front` });
    const backCheck = screen.getByRole("checkbox", { name: `${checkLabel}: Back` });
    expect(screen.getAllByText(checkLabel)).toHaveLength(2);
    expect(frontCheck).not.toBeChecked();
    expect(backCheck).not.toBeChecked();
    // Category chips retain their visible label as the default accessible name.
    expect(screen.getByRole("radio", { name: "Shirt" })).toBeChecked();
    await fireEvent.press(frontCheck);
    expect(frontCheck).toBeChecked();
    expect(backCheck).not.toBeChecked();
    expect(screen.getByRole("button", { name: "Continue" })).toBeDisabled();
    await fireEvent.press(backCheck);
    expect(backCheck).toBeChecked();
    expect(screen.getByRole("button", { name: "Continue" })).toBeEnabled();
  });

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
    expect(useIntakeStore.getState().inspirationMode).toBe("surprise");
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
        inspirationMode: "text",
        inspirationDraft: { imageUri: null, text: "shorter sleeves", surprisePrompt: null },
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
    const stored = useIntakeStore.getState().measurements.chest_flat_width!;
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
          ["chest_flat_width", "shoulder_to_hem", "shoulder_width", "sleeve_length"].map((k, i) => [
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
    expect(useIntakeStore.getState().measurements.chest_flat_width?.inputCm).toBe("52");

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

describe("review fixes", () => {
  const ready = async () =>
    act(() =>
      useIntakeStore.getState().patch({
        category: "shirt",
        front: photo,
        back: photo,
        inspirationMode: "text",
        inspirationDraft: { imageUri: null, text: "shorter sleeves", surprisePrompt: null },
        fit: "relaxed",
        skill: "beginner",
        measurements: Object.fromEntries(
          [
            ["chest_flat_width", "52"],
            ["shoulder_to_hem", "70"],
            ["shoulder_width", "45"],
            ["sleeve_length", "60"],
          ].map(([k, v]) => [
            k,
            { inputCm: v, confirmedAt: "2026-10-28T00:00:00Z", origin: "user_entered" },
          ]),
        ),
      }),
    );

  it("offers only the suggestion, not Keep, for a value outside the hard range", async () => {
    await ready();
    await renderScreen(<MeasurementsScreen />);
    await fireEvent.changeText(screen.getByLabelText("Chest, flat across (cm)"), "500");
    expect(screen.getByRole("button", { name: "Use 50 cm" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: /^Keep/ })).toBeNull();
  });

  it("marks an upload as stale after any later edit to photos or category", async () => {
    await ready();
    await act(() => useIntakeStore.getState().patch({ uploadStatus: "uploaded" }));
    await act(() => useIntakeStore.getState().patch({ role: "user" }));
    expect(useIntakeStore.getState().uploadStatus).toBe("uploaded");
    await act(() => useIntakeStore.getState().patch({ category: "dress" }));
    expect(useIntakeStore.getState().uploadStatus).toBe("not_uploaded");
    await act(() => useIntakeStore.getState().patch({ uploadStatus: "uploaded" }));
    await act(() => useIntakeStore.getState().patch({ front: { ...photo, uri: "file:///b.jpg" } }));
    expect(useIntakeStore.getState().uploadStatus).toBe("not_uploaded");
  });

  it("shows a mock marker beside an Uploaded status from the fixture client", async () => {
    await ready();
    await renderScreen(<MeasurementsScreen />);
    await fireEvent.press(screen.getByRole("button", { name: "Upload" }));
    expect(await screen.findByText(/^✓ Uploaded/)).toBeTruthy();
    expect(screen.getByLabelText("Sample data, not a real result")).toBeTruthy();
  });

  it("leaves body measurements out unless the user opts in, and then records the consent", async () => {
    await ready();
    const uploadIntake = jest.fn().mockResolvedValue(await mockApi.uploadIntake({} as never));
    setApi({ ...mockApi, uploadIntake });
    await act(() =>
      useIntakeStore.getState().setMeasurement("height", {
        inputCm: "170",
        confirmedAt: "2026-10-28T00:00:00Z",
        origin: "user_entered",
      }),
    );
    await renderScreen(<MeasurementsScreen />);
    expect(screen.queryByLabelText("Height (cm)")).toBeNull();
    await fireEvent.press(screen.getByRole("button", { name: "Upload" }));
    await waitFor(() => expect(uploadIntake).toHaveBeenCalledTimes(1));
    const first = uploadIntake.mock.calls[0]![0];
    expect(first.body_consent_version).toBeNull();
    expect(first.measurements.map((m: { key: string }) => m.key)).not.toContain("height");

    await fireEvent.press(screen.getByRole("checkbox", { name: /Include my body/ }));
    await fireEvent.press(screen.getByRole("button", { name: "Upload" }));
    await waitFor(() => expect(uploadIntake).toHaveBeenCalledTimes(2));
    const second = uploadIntake.mock.calls[1]![0];
    expect(second.body_consent_version).toBe("body-v0-draft");
    expect(second.measurements.map((m: { key: string }) => m.key)).toContain("height");
  });

  it("blocks upload while an opted-in body value is unconfirmed", async () => {
    await ready();
    const uploadIntake = jest.fn();
    setApi({ ...mockApi, uploadIntake });
    await act(() => useIntakeStore.getState().patch({ bodyConsentVersion: "body-v0-draft" }));
    await renderScreen(<MeasurementsScreen />);
    await fireEvent.changeText(screen.getByLabelText("Height (cm)"), "250");
    await fireEvent.press(screen.getByRole("button", { name: "Upload" }));
    expect(screen.getByText(/Confirm or clear before uploading: Height/)).toBeTruthy();
    expect(uploadIntake).not.toHaveBeenCalled();
  });

  it("keeps typed text when switching to Surprise Me and back, and submits only the selected mode", async () => {
    await renderScreen(<InspirationScreen />);
    await fireEvent.changeText(screen.getByLabelText("Describe the change you want"), "boxy crop");
    await fireEvent.press(screen.getByRole("radio", { name: "Surprise Me" }));
    await fireEvent.press(screen.getAllByRole("button", { name: "Surprise Me" })[0]!);
    expect(await screen.findByText(/^Idea:/)).toBeTruthy();
    await fireEvent.press(screen.getByRole("radio", { name: "Describe it" }));
    expect(screen.getByDisplayValue("boxy crop")).toBeTruthy();

    // Image mode with no image: hidden text must not count, Continue stays disabled.
    await fireEvent.press(screen.getByRole("radio", { name: "Image" }));
    await act(() => useIntakeStore.getState().patch({ fit: "relaxed", skill: "beginner" }));
    expect(screen.getByRole("button", { name: "Continue" })).toBeDisabled();
  });
});
