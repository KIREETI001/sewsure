import React, { useEffect, useState } from 'react';
import { StyleSheet, TextInput, View } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';
import { borderWidth, minTouchTarget, radius, spacing } from '../tokens/spacing';
import { maxFontScale, typeScale } from '../tokens/typography';
import { uiStrings } from '../strings';
import { Text } from './Text';

export type MeasurementInputProps = {
  label: string;
  /** Source of truth, in millimetres. null = not entered yet. */
  valueMm: number | null;
  /** Called with the new value in mm (rounded to 0.1 mm), or null when cleared/invalid. */
  onChangeMm: (mm: number | null) => void;
  errorText?: string;
  helperText?: string;
  testID?: string;
};

const mmToCmText = (mm: number | null) => (mm == null ? '' : String(Math.round(mm) / 10));

/** Parses a user-typed cm string (accepts "," decimal) into mm, or null. */
export function parseCmToMm(text: string): number | null {
  const normalised = text.trim().replace(',', '.');
  if (normalised === '' || !/^\d*\.?\d+$|^\d+\.$/.test(normalised)) return null;
  const cm = Number(normalised);
  if (!Number.isFinite(cm) || cm < 0) return null;
  return Math.round(cm * 100) / 10;
}

/** Shows and edits centimetres; the stored and emitted value stays in millimetres. */
export function MeasurementInput({
  label,
  valueMm,
  onChangeMm,
  errorText,
  helperText,
  testID,
}: MeasurementInputProps) {
  const { colors } = useTheme();
  const [text, setText] = useState(mmToCmText(valueMm));

  // Re-sync when the parent changes the value to something the text doesn't represent.
  useEffect(() => {
    if (parseCmToMm(text) !== valueMm) setText(mmToCmText(valueMm));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [valueMm]);

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
          testID={testID}
          value={text}
          onChangeText={(t) => {
            setText(t);
            onChangeMm(parseCmToMm(t));
          }}
          keyboardType="decimal-pad"
          allowFontScaling
          maxFontSizeMultiplier={maxFontScale}
          accessibilityLabel={`${label}, ${uiStrings.unitCm}`}
          accessibilityHint={valueMm != null ? uiStrings.mmStored(valueMm) : undefined}
          accessibilityState={{ disabled: false }}
          style={[styles.input, typeScale.body, { color: colors.text }]}
          placeholderTextColor={colors.textSecondary}
        />
        <Text variant="bodyStrong" tone="secondary" importantForAccessibility="no">
          {uiStrings.unitCm}
        </Text>
      </View>
      {hint ? (
        <Text variant="caption" tone={errorText ? 'danger' : 'secondary'}>
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
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: borderWidth.control,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
  },
  input: { flex: 1, minHeight: minTouchTarget, paddingVertical: spacing.sm },
});
