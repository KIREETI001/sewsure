import { useLocalSearchParams } from "expo-router";
import { useEffect, useRef, useState } from "react";
import { Button, Text, View } from "react-native";
import CaptureScreen from "../../app/(intake)/capture";
import InspirationScreen from "../../app/(intake)/inspiration";
import MeasurementsScreen from "../../app/(intake)/measurements";
import { useIntakeStore } from "@/state/intakeStore";
import { applyIntakeSeed, INTAKE_SEED_NAMES, type IntakeSeedName } from "./intakeSeeds";
import { installMockUploadFailure } from "./mockUploadFailure";

export function parseSeedName(value: string | string[] | undefined): IntakeSeedName | null {
  return typeof value === "string" && INTAKE_SEED_NAMES.some((name) => name === value)
    ? (value as IntakeSeedName)
    : null;
}

/** Imported only by the generated, build-gated QA route. */
export default function SeedRoute() {
  const params = useLocalSearchParams<{ name?: string | string[] }>();
  const name = parseSeedName(params.name);
  // A different link gets a new one-shot lifecycle; re-renders never reset user edits.
  return name ? <SeedSession key={name} name={name} /> : <Text>Invalid seed name</Text>;
}

function SeedSession({ name }: { name: IntakeSeedName }) {
  const applied = useRef(false);
  const [ready, setReady] = useState(false);
  const failure = useRef<ReturnType<typeof installMockUploadFailure> | null>(null);
  const [failureStatus, setFailureStatus] = useState("disabled");
  useEffect(
    () => () => {
      failure.current?.dispose();
      failure.current = null;
    },
    [],
  );
  const toggleFailure = (enabled: boolean) => {
    try {
      if (enabled) {
        failure.current ??= installMockUploadFailure();
        failure.current.setFailure(true);
      } else {
        failure.current?.dispose();
        failure.current = null;
      }
      setFailureStatus(enabled ? "enabled" : "disabled");
    } catch {
      setFailureStatus("unavailable: default mock API required");
    }
  };
  useEffect(() => {
    const apply = () => {
      if (applied.current) return;
      applied.current = true;
      applyIntakeSeed(name, useIntakeStore.getState());
      setReady(true);
    };
    const unsubscribe = useIntakeStore.persist.onFinishHydration(apply);
    if (useIntakeStore.persist.hasHydrated()) apply();
    return unsubscribe;
  }, [name]);

  if (!ready) return <Text>Waiting for intake hydration</Text>;
  return (
    <View style={{ flex: 1 }}>
      <Text accessibilityRole="header">{`Seeded: ${name}`}</Text>
      <Text>{`Mock upload failure: ${failureStatus}`}</Text>
      <Button title="Enable mock upload failure" onPress={() => toggleFailure(true)} />
      <Button title="Disable mock upload failure" onPress={() => toggleFailure(false)} />
      {name === "capture-ready" ? (
        <CaptureScreen />
      ) : name === "inspiration-ready" ? (
        <InspirationScreen />
      ) : (
        <MeasurementsScreen />
      )}
    </View>
  );
}
