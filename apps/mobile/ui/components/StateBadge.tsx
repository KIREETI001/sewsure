import React from 'react';
import { StyleSheet, View } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';
import { borderWidth, radius, spacing } from '../tokens/spacing';
import { uiStrings } from '../strings';
import { Text } from './Text';

/**
 * The three user-facing design states. This component only DISPLAYS a state
 * decided by the feasibility engine; it never derives or upgrades one.
 */
export type DesignStateKind = 'verified' | 'needs_info' | 'inspiration';

const config = {
  verified: { symbol: '✓', label: uiStrings.stateVerified, key: 'stateVerified' },
  needs_info: { symbol: '?', label: uiStrings.stateNeedsInfo, key: 'stateNeedsInfo' },
  inspiration: { symbol: '✦', label: uiStrings.stateInspiration, key: 'stateInspiration' },
} as const;

export type StateBadgeProps = {
  state: DesignStateKind;
  /** Override the visible text (e.g. from the i18n catalogue). */
  label?: string;
};

export function StateBadge({ state, label }: StateBadgeProps) {
  const { colors } = useTheme();
  const c = config[state];
  const palette = colors[c.key];
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
    alignSelf: 'flex-start',
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    borderWidth: borderWidth.control,
  },
});
