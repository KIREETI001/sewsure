import React from "react";
import { ActivityIndicator, Pressable, StyleSheet, type PressableProps } from "react-native";
import { useTheme } from "../theme/ThemeProvider";
import { borderWidth, minTouchTarget, radius, spacing } from "../tokens/spacing";
import { Text } from "./Text";

export type ButtonProps = Omit<PressableProps, "children" | "style"> & {
  label: string;
  variant?: "primary" | "secondary" | "danger";
  loading?: boolean;
  /** Overrides the spoken label; defaults to `label`. */
  accessibilityLabel?: string;
  accessibilityHint?: string;
};

export function Button({
  label,
  variant = "primary",
  loading = false,
  disabled,
  accessibilityLabel,
  accessibilityHint,
  ...rest
}: ButtonProps) {
  const { colors } = useTheme();
  const isDisabled = Boolean(disabled) || loading;
  const palette =
    variant === "primary"
      ? { bg: colors.primary, fg: colors.onPrimary, border: colors.primary }
      : variant === "danger"
        ? { bg: colors.surface, fg: colors.danger, border: colors.danger }
        : { bg: colors.surface, fg: colors.primary, border: colors.border };

  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel ?? label}
      accessibilityHint={accessibilityHint}
      accessibilityState={{ disabled: isDisabled, busy: loading }}
      disabled={isDisabled}
      hitSlop={0}
      style={({ pressed, focused }: { pressed: boolean; focused?: boolean }) => [
        styles.base,
        {
          backgroundColor: palette.bg,
          borderColor: focused ? colors.focusRing : palette.border,
          opacity: isDisabled ? 0.55 : pressed ? 0.85 : 1,
        },
      ]}
      {...rest}
    >
      {loading ? <ActivityIndicator color={palette.fg} /> : null}
      <Text variant="bodyStrong" style={{ color: palette.fg, textAlign: "center" }}>
        {label}
      </Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    minHeight: minTouchTarget,
    minWidth: minTouchTarget,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.sm,
    borderRadius: radius.md,
    borderWidth: borderWidth.control,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
  },
});
