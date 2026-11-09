import { Stack } from "expo-router";
import { tm } from "@/make/i18n";

export default function MakeLayout() {
  return (
    <Stack>
      <Stack.Screen name="cut" options={{ title: tm("make.cut.title") }} />
      <Stack.Screen name="diy" options={{ title: tm("make.diy.title") }} />
    </Stack>
  );
}
