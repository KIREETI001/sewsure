import { Stack } from "expo-router";
import { t } from "@/i18n";
import { ThemeProvider } from "../../ui";

export default function StudioLayout() {
  return (
    <ThemeProvider>
      <Stack>
        <Stack.Screen name="generating" options={{ title: t("studio.generating.title") }} />
        <Stack.Screen name="results" options={{ title: t("studio.results.title") }} />
        <Stack.Screen name="design" options={{ title: t("studio.design.title") }} />
      </Stack>
    </ThemeProvider>
  );
}
