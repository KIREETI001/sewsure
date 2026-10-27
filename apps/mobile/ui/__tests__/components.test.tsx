/**
 * Written to run once D2's scaffold provides Jest (jest-expo) and
 * @testing-library/react-native. Not run in this PR (no package.json yet).
 */
import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react-native';
import {
  Button,
  ChecklistItem,
  Card,
  MeasurementInput,
  MockBadge,
  StateBadge,
  StepCard,
  ThemeProvider,
  minTouchTarget,
  parseCmToMm,
  uiStrings,
} from '..';
import { Text } from 'react-native';

const wrap = (ui: React.ReactElement) => render(<ThemeProvider scheme="light">{ui}</ThemeProvider>);

describe('Button', () => {
  it('is a labelled button and fires onPress', () => {
    const onPress = jest.fn();
    wrap(<Button label="Continue" onPress={onPress} />);
    fireEvent.press(screen.getByRole('button', { name: 'Continue' }));
    expect(onPress).toHaveBeenCalledTimes(1);
  });

  it('is not pressable and reports disabled/busy while loading', () => {
    const onPress = jest.fn();
    wrap(<Button label="Save" loading onPress={onPress} />);
    const button = screen.getByRole('button', { name: 'Save' });
    expect(button.props.accessibilityState).toMatchObject({ disabled: true, busy: true });
    fireEvent.press(button);
    expect(onPress).not.toHaveBeenCalled();
  });

  it('meets the minimum touch target', () => {
    wrap(<Button label="Go" />);
    const style = [screen.getByRole('button', { name: 'Go' }).props.style].flat(2);
    const merged = Object.assign({}, ...style.filter(Boolean));
    expect(merged.minHeight).toBeGreaterThanOrEqual(minTouchTarget);
  });
});

describe('StateBadge', () => {
  it.each([
    ['verified', uiStrings.stateVerified, '✓'],
    ['needs_info', uiStrings.stateNeedsInfo, '?'],
    ['inspiration', uiStrings.stateInspiration, '✦'],
  ] as const)('%s shows text and a symbol', (state, label, symbol) => {
    wrap(<StateBadge state={state} />);
    expect(screen.getByText(label)).toBeTruthy();
    expect(screen.getByText(symbol)).toBeTruthy();
    expect(screen.getByLabelText(`${uiStrings.stateAccessibilityPrefix}: ${label}`)).toBeTruthy();
  });

  it('never uses guarantee wording', () => {
    const all = [uiStrings.stateVerified, uiStrings.stateNeedsInfo, uiStrings.stateInspiration].join(' ');
    expect(all).not.toMatch(/guarantee|perfect fit|100%|safe to cut/i);
  });
});

describe('MockBadge', () => {
  it('is visible text with an explanatory accessibility label', () => {
    wrap(<MockBadge />);
    expect(screen.getByText(/MOCK DATA/)).toBeTruthy();
    expect(screen.getByLabelText(uiStrings.mockAccessibility)).toBeTruthy();
  });
});

describe('parseCmToMm', () => {
  it.each([
    ['50', 500],
    ['50.5', 505],
    ['50,5', 505],
    ['0.1', 1],
    ['', null],
    ['abc', null],
    ['-3', null],
    ['1.2.3', null],
  ])('%p -> %p', (input, expected) => {
    expect(parseCmToMm(input)).toBe(expected);
  });
});

describe('MeasurementInput', () => {
  it('displays cm for an mm value and labels the unit', () => {
    wrap(<MeasurementInput label="Waist" valueMm={825} onChangeMm={() => {}} />);
    const input = screen.getByLabelText('Waist, cm');
    expect(input.props.value).toBe('82.5');
    expect(screen.getByText('cm')).toBeTruthy();
  });

  it('emits millimetres when the user types centimetres', () => {
    const onChangeMm = jest.fn();
    wrap(<MeasurementInput label="Waist" valueMm={null} onChangeMm={onChangeMm} />);
    fireEvent.changeText(screen.getByLabelText('Waist, cm'), '82,5');
    expect(onChangeMm).toHaveBeenLastCalledWith(825);
    fireEvent.changeText(screen.getByLabelText('Waist, cm'), 'x');
    expect(onChangeMm).toHaveBeenLastCalledWith(null);
  });

  it('shows an error with a non-colour marker', () => {
    wrap(<MeasurementInput label="Waist" valueMm={null} onChangeMm={() => {}} errorText="Enter a number" />);
    expect(screen.getByText('! Enter a number')).toBeTruthy();
  });
});

describe('ChecklistItem', () => {
  it('exposes checkbox role and checked state, and toggles', () => {
    const onToggle = jest.fn();
    wrap(<ChecklistItem label="Pre-wash fabric" checked={false} onToggle={onToggle} />);
    const item = screen.getByRole('checkbox', { name: 'Pre-wash fabric' });
    expect(item.props.accessibilityState).toMatchObject({ checked: false });
    fireEvent.press(item);
    expect(onToggle).toHaveBeenCalledWith(true);
  });

  it('shows a tick symbol when checked', () => {
    wrap(<ChecklistItem label="Pre-wash fabric" checked onToggle={() => {}} />);
    expect(screen.getByText('✓')).toBeTruthy();
  });
});

describe('StepCard', () => {
  it('announces step number, title and status, with a symbol for status', () => {
    wrap(<StepCard stepNumber={2} totalSteps={5} title="Mark the cut line" body="Use chalk." done />);
    expect(screen.getByLabelText(/Step 2 of 5\. Mark the cut line\. Done\. Use chalk\./)).toBeTruthy();
    expect(screen.getByText('✓ Done')).toBeTruthy();
  });

  it('marks not-done steps with text and a symbol', () => {
    wrap(<StepCard stepNumber={1} totalSteps={5} title="Prepare" body="Lay flat." />);
    expect(screen.getByText('○ Not done')).toBeTruthy();
  });
});

describe('Card', () => {
  it('renders children', () => {
    wrap(
      <Card>
        <Text>inside</Text>
      </Card>,
    );
    expect(screen.getByText('inside')).toBeTruthy();
  });
});
