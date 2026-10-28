import React from "react";
import { StyleSheet, View, type ViewProps } from "react-native";
import { useTheme } from "../theme/ThemeProvider";
import { borderWidth, radius, spacing } from "../tokens/spacing";

export type CardProps = ViewProps & {
  /** Group the card's content as one screen-reader element. Default false. */
  accessible?: boolean;
  accessibilityLabel?: string;
};

export function Card({ style, children, ...rest }: CardProps) {
  const { colors } = useTheme();
  return (
    <View
      style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.divider }, style]}
      {...rest}
    >
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: spacing.lg,
    borderRadius: radius.md,
    borderWidth: borderWidth.hairline,
    gap: spacing.sm,
  },
});
