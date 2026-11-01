import React from "react";
import { StyleSheet, TextInput, View, type TextInputProps } from "react-native";
import { useTheme } from "../theme/ThemeProvider";
import { borderWidth, minTouchTarget, radius, spacing } from "../tokens/spacing";
import { maxFontScale, typeScale } from "../tokens/typography";
import { uiStrings } from "../strings";
import { Text } from "./Text";

export type CmParse =
  { status: "empty"; mm: null } | { status: "invalid"; mm: null } | { status: "ok"; mm: number };

/**
 * Parses text typed in centimetres ("60", "60.5", "60,5") into millimetres
 * (0.1 mm precision). Zero, negatives, ".5", units and ranges are invalid.
 * Same grammar as D2's `parseCm`, so the two can be merged without behaviour change.
 */
export function parseCmToMm(text: string): CmParse {
  const trimmed = text.trim();
  if (trimmed === "") return { status: "empty", mm: null };
  if (!/^\d+([.,]\d+)?$/.test(trimmed)) return { status: "invalid", mm: null };
  const cm = Number(trimmed.replace(",", "."));
  if (!Number.isFinite(cm) || cm <= 0) return { status: "invalid", mm: null };
  return { status: "ok", mm: Math.round(cm * 100) / 10 };
}

export type MeasurementChange = { text: string } & CmParse;

export type MeasurementInputProps = Omit<
  TextInputProps,
  "value" | "onChange" | "onChangeText" | "style" | "keyboardType"
> & {
  label: string;
  /** The text as typed, in centimetres. The caller stores it (local draft). */
  text: string;
  /** Emits the typed text plus its millimetre value and parse status. */
  onChange: (change: MeasurementChange) => void;
  errorText?: string;
  helperText?: string;
};

/**
 * Shows and edits centimetres; emits millimetres. Controlled and stateless, so
 * the caller decides when a value is confirmed (e.g. `onBlur`) and owns origin
 * and `confirmed_at`. All other TextInput props (onBlur, onFocus, ...) pass through.
 */
export function MeasurementInput({
  label,
  text,
  onChange,
  errorText,
  helperText,
  ...inputProps
}: MeasurementInputProps) {
  const { colors } = useTheme();
  const parsed = parseCmToMm(text);
  const hint = errorText ?? helperText;
  return (
    <View style={styles.wrap}>
      <Text variant="label">{label}</Text>
      <View
        style={[
          styles.row,
          {
            backgroundColor: colors.surface,
            borderColor: errorText ? colors.danger : colors.border,
          },
        ]}
      >
        <TextInput
          allowFontScaling
          maxFontSizeMultiplier={maxFontScale}
          accessibilityLabel={`${label}, ${uiStrings.unitCm}`}
          accessibilityHint={parsed.status === "ok" ? uiStrings.mmStored(parsed.mm) : undefined}
          placeholderTextColor={colors.textSecondary}
          {...inputProps}
          value={text}
          onChangeText={(t) => onChange({ text: t, ...parseCmToMm(t) })}
          keyboardType="decimal-pad"
          style={[styles.input, typeScale.body, { color: colors.text }]}
        />
        <Text variant="bodyStrong" tone="secondary" importantForAccessibility="no">
          {uiStrings.unitCm}
        </Text>
      </View>
      {hint ? (
        <Text variant="caption" tone={errorText ? "danger" : "secondary"}>
          {errorText ? `! ${hint}` : hint}
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: spacing.xs },
  row: {
    minHeight: minTouchTarget,
    flexDirection: "row",
    alignItems: "center",
    borderWidth: borderWidth.control,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
  },
  input: { flex: 1, minHeight: minTouchTarget, paddingVertical: spacing.sm },
});
