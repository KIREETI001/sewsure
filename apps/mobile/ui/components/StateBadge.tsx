import React from "react";
import { StyleSheet, View } from "react-native";
import { useTheme } from "../theme/ThemeProvider";
import { borderWidth, radius, spacing } from "../tokens/spacing";
import type { StateColors } from "../tokens/colors";
import { uiStrings } from "../strings";
import { Text } from "./Text";

/**
 * Design states exactly as defined by the contract
 * (packages/contracts/schemas/design-state.schema.json). Set only by the
 * feasibility engine. This component DISPLAYS a state; it never derives,
 * maps or upgrades one, so screens pass the API value straight through.
 */
export type DesignState =
  "IDEA_ONLY" | "NEEDS_INPUT" | "FAILED_CHECKS" | "PASS_SUPPORTED_CHECKS" | "SUPERSEDED";

type Config = {
  symbol: string;
  label: string;
  color:
    "stateVerified" | "stateNeedsInfo" | "stateInspiration" | "stateFailed" | "stateSuperseded";
};

const config: Record<DesignState, Config> = {
  PASS_SUPPORTED_CHECKS: { symbol: "✓", label: uiStrings.stateVerified, color: "stateVerified" },
  NEEDS_INPUT: { symbol: "?", label: uiStrings.stateNeedsInfo, color: "stateNeedsInfo" },
  IDEA_ONLY: { symbol: "✦", label: uiStrings.stateInspiration, color: "stateInspiration" },
  FAILED_CHECKS: { symbol: "✗", label: uiStrings.stateFailed, color: "stateFailed" },
  SUPERSEDED: { symbol: "↺", label: uiStrings.stateSuperseded, color: "stateSuperseded" },
};

export type StateBadgeProps = {
  state: DesignState;
  /** Override the visible text (e.g. from the i18n catalogue). */
  label?: string;
};

export function StateBadge({ state, label }: StateBadgeProps) {
  const { colors } = useTheme();
  const c = config[state];
  const palette: StateColors = colors[c.color];
  const text = label ?? c.label;
  return (
    <View
      accessible
      accessibilityRole="text"
      accessibilityLabel={`${uiStrings.stateAccessibilityPrefix}: ${text}`}
      style={[styles.badge, { backgroundColor: palette.bg, borderColor: palette.border }]}
    >
      {/* Symbol is decorative for screen readers; the label carries the meaning. */}
      <Text
        importantForAccessibility="no"
        accessibilityElementsHidden
        variant="label"
        style={{ color: palette.fg }}
      >
        {c.symbol}
      </Text>
      <Text variant="label" style={{ color: palette.fg, flexShrink: 1 }}>
        {text}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    alignSelf: "flex-start",
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    borderWidth: borderWidth.control,
  },
});
