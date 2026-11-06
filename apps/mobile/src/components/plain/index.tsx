/**
 * Plain React Native stand-ins for the design system.
 * REPLACE with D1's components from apps/mobile/ui when they land: Screen, Heading, Button,
 * Chip, TextField, Notice and MockBadge each map to one D1 component.
 * Every control keeps a 44 pt minimum touch target and a screen-reader label.
 */
import type { ReactNode } from "react";
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
  type TextInputProps,
} from "react-native";
import { t } from "@/i18n";

export const colors = {
  ink: "#1b1b1f",
  muted: "#5a5a63",
  line: "#c9c9d1",
  accent: "#2f4bd1",
  bg: "#ffffff",
  warnBg: "#fff4d6",
  errBg: "#fde4e4",
};

export function Screen({ children }: { children: ReactNode }) {
  return (
    <ScrollView contentContainerStyle={styles.screen} keyboardShouldPersistTaps="handled">
      {children}
    </ScrollView>
  );
}

export function Heading({ children }: { children: string }) {
  return (
    <Text accessibilityRole="header" style={styles.heading}>
      {children}
    </Text>
  );
}

export function Body({ children, muted }: { children: ReactNode; muted?: boolean }) {
  return <Text style={[styles.body, muted && { color: colors.muted }]}>{children}</Text>;
}

export function Button({
  label,
  onPress,
  disabled,
  secondary,
  accessibilityLabel,
}: {
  label: string;
  onPress: () => void;
  disabled?: boolean;
  secondary?: boolean;
  accessibilityLabel?: string;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel ?? label}
      accessibilityState={{ disabled: !!disabled }}
      disabled={disabled}
      onPress={onPress}
      style={[styles.button, secondary && styles.buttonSecondary, disabled && styles.disabled]}
    >
      <Text style={[styles.buttonText, secondary && { color: colors.accent }]}>{label}</Text>
    </Pressable>
  );
}

/** Selectable option. Selection is shown by a tick symbol as well as styling. */
export function Chip({
  label,
  selected,
  onPress,
  role = "radio",
  accessibilityLabel,
}: {
  label: string;
  selected: boolean;
  onPress: () => void;
  role?: "radio" | "checkbox";
  accessibilityLabel?: string;
}) {
  return (
    <Pressable
      accessibilityRole={role}
      accessibilityLabel={accessibilityLabel ?? label}
      accessibilityState={{ checked: selected }}
      onPress={onPress}
      style={[styles.chip, selected && styles.chipSelected]}
    >
      <Text style={styles.chipText}>{selected ? `✓ ${label}` : label}</Text>
    </Pressable>
  );
}

export function TextField({
  label,
  hint,
  ...input
}: { label: string; hint?: string } & TextInputProps) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      {hint ? <Body muted>{hint}</Body> : null}
      <TextInput
        accessibilityLabel={label}
        accessibilityHint={hint}
        style={styles.input}
        placeholderTextColor={colors.muted}
        {...input}
      />
    </View>
  );
}

export function Notice({
  children,
  tone = "warn",
}: {
  children: ReactNode;
  tone?: "warn" | "error" | "info";
}) {
  const bg = tone === "error" ? colors.errBg : tone === "warn" ? colors.warnBg : "#e8edff";
  const symbol = tone === "error" ? "✗" : tone === "warn" ? "!" : "i";
  return (
    <View accessibilityRole="alert" style={[styles.notice, { backgroundColor: bg }]}>
      <Text style={styles.body}>{`${symbol}  `}</Text>
      <View style={{ flex: 1 }}>{children}</View>
    </View>
  );
}

/** Marks anything rendered from fixture data. */
export function MockBadge() {
  return (
    <View accessible accessibilityLabel={t("common.mockHint")} style={styles.mock}>
      <Text style={styles.mockText}>{t("common.mock")}</Text>
    </View>
  );
}

export function Row({ children }: { children: ReactNode }) {
  return <View style={styles.row}>{children}</View>;
}

const styles = StyleSheet.create({
  screen: { padding: 16, gap: 14, backgroundColor: colors.bg, flexGrow: 1 },
  heading: { fontSize: 22, fontWeight: "700", color: colors.ink },
  body: { fontSize: 16, color: colors.ink },
  button: {
    minHeight: 48,
    minWidth: 44,
    borderRadius: 8,
    backgroundColor: colors.accent,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  buttonSecondary: { backgroundColor: colors.bg, borderWidth: 1, borderColor: colors.accent },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "600", textAlign: "center" },
  disabled: { opacity: 0.45 },
  chip: {
    minHeight: 44,
    minWidth: 44,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: colors.line,
    paddingHorizontal: 14,
    justifyContent: "center",
  },
  chipSelected: { borderColor: colors.accent, backgroundColor: "#e8edff" },
  chipText: { fontSize: 15, color: colors.ink },
  field: { gap: 4 },
  label: { fontSize: 15, fontWeight: "600", color: colors.ink },
  input: {
    minHeight: 48,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 8,
    paddingHorizontal: 12,
    fontSize: 16,
    color: colors.ink,
  },
  notice: { flexDirection: "row", padding: 12, borderRadius: 8, gap: 4 },
  mock: {
    alignSelf: "flex-start",
    borderWidth: 1,
    borderColor: colors.muted,
    borderStyle: "dashed",
    borderRadius: 4,
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  mockText: { fontSize: 12, color: colors.muted, fontWeight: "700" },
  row: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
});
