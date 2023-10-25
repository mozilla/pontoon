import { createContext, useState } from 'react';
import { useTheme } from '~/hooks/useTheme';

export const ThemeContext = createContext({
  theme: 'system',
});

export function ThemeProvider({ children }: { children: React.ReactElement }) {
  const [theme] = useState(
    () => document.body.getAttribute('data-theme') || 'dark',
  );

  useTheme(theme);

  return (
    <ThemeContext.Provider value={{ theme }}>{children}</ThemeContext.Provider>
  );
}
