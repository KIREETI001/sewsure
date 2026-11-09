import React from "react";
import { StyleSheet, View } from "react-native";
import { useTheme } from "../theme/ThemeProvider";
import { borderWidth, radius, spacing } from "../tokens/spacing";
import { uiStrings } from "../strings";
import { Text } from "./Text";
import { isLocalJourney } from "../../src/api/localTransport";
import { t } from "../../src/i18n";

/** Marks anything rendered from a fixture rather than a real API result. */
export function MockBadge({ label = uiStrings.mock }: { label?: string }) {
  const { colors } = useTheme();
  const local = isLocalJourney();
  return (
    <View
      accessible
      accessibilityRole="text"
      accessibilityLabel={local ? t("local.badgeHint") : uiStrings.mockAccessibility}
      style={[styles.badge, { backgroundColor: colors.mock.bg, borderColor: colors.mock.border }]}
    >
      <Text variant="caption" style={{ color: colors.mock.fg, fontWeight: "700" }}>
        {`⚠ ${local ? t("local.badge") : label}`}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    alignSelf: "flex-start",
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.sm,
    borderWidth: borderWidth.hairline,
  },
});
