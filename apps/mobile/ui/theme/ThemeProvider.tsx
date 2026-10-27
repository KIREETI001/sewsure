import React, { createContext, useContext, useMemo } from 'react';
import { useColorScheme } from 'react-native';
import { colorSchemes, type ColorScheme, type ColorTokens } from '../tokens/colors';

type Theme = { scheme: ColorScheme; colors: ColorTokens };

const ThemeContext = createContext<Theme | null>(null);

/** Follows the OS scheme unless `scheme` is forced (tests, previews). */
export function ThemeProvider({
  scheme,
  children,
}: {
  scheme?: ColorScheme;
  children: React.ReactNode;
}) {
  const system = useColorScheme();
  const resolved: ColorScheme = scheme ?? (system === 'dark' ? 'dark' : 'light');
  const value = useMemo(() => ({ scheme: resolved, colors: colorSchemes[resolved] }), [resolved]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): Theme {
  const theme = useContext(ThemeContext);
  if (!theme) return { scheme: 'light', colors: colorSchemes.light };
  return theme;
}
