import { createContext, useState } from 'react';
import { useTheme } from '~/hooks/useTheme';

export const ThemeContext = createContext({
  theme: 'dark',
  setTheme: (_theme: string) => {}, // placeholder function to match signature
});

export function ThemeProvider({ children }: { children: React.ReactElement }) {
  const [theme, setTheme] = useState(
    () => document.body.getAttribute('data-theme') || 'dark',
  );
  const { applyTheme } = useTheme();

  applyTheme(theme);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
