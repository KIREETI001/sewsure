import { ScrollView, View } from "react-native";
import { Button, MockBadge, Text } from "../../../ui";
import { tm } from "../i18n";
import type { MakeBundle } from "../types";

export function Loading() {
  return <Text style={{ padding: 16 }}>{tm("make.loading")}</Text>;
}

export function LoadFailed({ onRetry }: { onRetry: () => void }) {
  return (
    <View style={{ padding: 16, gap: 12 }}>
      <Text tone="danger">{tm("make.loadFailed")}</Text>
      <Button label={tm("make.retry")} onPress={onRetry} />
    </View>
  );
}

export function Page({ bundle, children }: { bundle: MakeBundle; children: React.ReactNode }) {
  return (
    <ScrollView contentContainerStyle={{ padding: 16, gap: 12 }}>
      {bundle.provenance === "mock" ? <MockBadge /> : null}
      {children}
    </ScrollView>
  );
}

export function DraftBanner() {
  return (
    <View accessible accessibilityRole="alert" testID="draft-banner" style={{ borderWidth: 2, padding: 12 }}>
      <Text variant="bodyStrong">{`⚠ ${tm("make.draft.badge")}`}</Text>
      <Text>{tm("make.draft.banner")}</Text>
    </View>
  );
}
