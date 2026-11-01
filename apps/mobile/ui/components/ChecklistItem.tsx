import React from "react";
import { Pressable, StyleSheet, View } from "react-native";
import { useTheme } from "../theme/ThemeProvider";
import { borderWidth, minTouchTarget, radius, spacing } from "../tokens/spacing";
import { Text } from "./Text";

export type ChecklistItemProps = {
  label: string;
  checked: boolean;
  onToggle: (next: boolean) => void;
  disabled?: boolean;
  description?: string;
};

export function ChecklistItem({
  label,
  checked,
  onToggle,
  disabled,
  description,
}: ChecklistItemProps) {
  const { colors } = useTheme();
  return (
    <Pressable
      accessibilityRole="checkbox"
      accessibilityLabel={label}
      accessibilityHint={description}
      accessibilityState={{ checked, disabled: Boolean(disabled) }}
      disabled={disabled}
      onPress={() => onToggle(!checked)}
      style={[styles.row, { opacity: disabled ? 0.55 : 1 }]}
    >
      <View
        style={[
          styles.box,
          {
            borderColor: colors.border,
            backgroundColor: checked ? colors.primary : colors.surface,
          },
        ]}
      >
        <Text
          importantForAccessibility="no"
          accessibilityElementsHidden
          variant="bodyStrong"
          style={{ color: colors.onPrimary }}
        >
          {checked ? "✓" : ""}
        </Text>
      </View>
      <View style={styles.text}>
        <Text>{label}</Text>
        {description ? (
          <Text variant="caption" tone="secondary">
            {description}
          </Text>
        ) : null}
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  row: {
    minHeight: minTouchTarget,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    paddingVertical: spacing.xs,
  },
  box: {
    width: 28,
    height: 28,
    borderRadius: radius.sm,
    borderWidth: borderWidth.control,
    alignItems: "center",
    justifyContent: "center",
  },
  text: { flex: 1 },
});
