import React from 'react';
import { Text as RNText, type TextProps } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';
import { maxFontScale, typeScale, type TextVariant } from '../tokens/typography';

export type UITextProps = TextProps & {
  variant?: TextVariant;
  tone?: 'default' | 'secondary' | 'danger';
};

/** Themed text that scales with the OS font size, capped at 200%. */
export function Text({ variant = 'body', tone = 'default', style, ...rest }: UITextProps) {
  const { colors } = useTheme();
  const color =
    tone === 'secondary' ? colors.textSecondary : tone === 'danger' ? colors.danger : colors.text;
  return (
    <RNText
      allowFontScaling
      maxFontSizeMultiplier={maxFontScale}
      style={[typeScale[variant], { color }, style]}
      {...rest}
    />
  );
}
