import React from 'react';
import { StyleSheet, View } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';
import { spacing } from '../tokens/spacing';
import { uiStrings } from '../strings';
import { Card } from './Card';
import { Text } from './Text';

export type StepCardProps = {
  stepNumber: number;
  totalSteps: number;
  title: string;
  body: string;
  done?: boolean;
  children?: React.ReactNode;
};

/** One DIY step. Completion is shown by text and a symbol, not colour alone. */
export function StepCard({ stepNumber, totalSteps, title, body, done = false, children }: StepCardProps) {
  const { colors } = useTheme();
  const status = done ? uiStrings.stepDone : uiStrings.stepNotDone;
  return (
    <Card
      accessible
      accessibilityRole="summary"
      accessibilityLabel={`${uiStrings.stepOf(stepNumber, totalSteps)}. ${title}. ${status}. ${body}`}
    >
      <View style={styles.header}>
        <Text variant="label" tone="secondary">
          {uiStrings.stepOf(stepNumber, totalSteps)}
        </Text>
        <Text variant="label" style={{ color: done ? colors.stateVerified.fg : colors.textSecondary }}>
          {done ? `✓ ${status}` : `○ ${status}`}
        </Text>
      </View>
      <Text variant="heading">{title}</Text>
      <Text>{body}</Text>
      {children}
    </Card>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: 'row', justifyContent: 'space-between', gap: spacing.sm },
});
