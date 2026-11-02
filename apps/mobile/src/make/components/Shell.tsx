import { ScrollView, View } from "react-native";
import { Button, MockBadge, Text } from "../../../ui";
import { tm, type MakeKey } from "../i18n";
import type { BlockedReason } from "../gate";
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

/** Closed screen with no bundle behind it (no id, unknown id). Shows a reason and a way back. */
export function GateNotice({ reason, onBack }: { reason: "no_revision" | "not_found"; onBack: () => void }) {
  const key: MakeKey = reason === "no_revision" ? "make.gate.reason.no_revision" : "make.gate.reason.not_found";
  return (
    <ScrollView contentContainerStyle={{ padding: 16, gap: 12 }}>
      <Text variant="heading">{tm("make.gate.title")}</Text>
      <Text testID="gate-reason">{tm(key)}</Text>
      <Button variant="secondary" label={tm("make.back")} onPress={onBack} />
    </ScrollView>
  );
}

/** Draft or unusable recipe: say which, and give a way out. Never a dead end. */
export function BlockedGuide({ reason, onBack }: { reason: BlockedReason; onBack: () => void }) {
  return (
    <View style={{ gap: 12 }}>
      <Text testID="draft-blocked">{tm(`make.blocked.${reason}` as const)}</Text>
      <Button variant="secondary" label={tm("make.back")} onPress={onBack} />
    </View>
  );
}
