import { Stack } from "expo-router";
import { t } from "@/i18n";

export default function IntakeLayout() {
  return (
    <Stack>
      <Stack.Screen name="index" options={{ title: "SewSure" }} />
      <Stack.Screen name="capture" options={{ title: t("capture.title") }} />
      <Stack.Screen name="inspiration" options={{ title: t("inspiration.title") }} />
      <Stack.Screen name="measurements" options={{ title: t("measure.title") }} />
    </Stack>
  );
}
