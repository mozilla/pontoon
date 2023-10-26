import { createContext, useEffect, useState } from 'react';
import { useTheme } from '~/hooks/useTheme';

export const ThemeContext = createContext({
  theme: 'dark',
});

export function ThemeProvider({ children }: { children: React.ReactElement }) {
  const [theme] = useState(
    () => document.body.getAttribute('data-theme') || 'dark',
  );

  const applyTheme = useTheme();

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    function handleThemeChange(e: MediaQueryListEvent) {
      let userThemeSetting = document.body.getAttribute('data-theme') || 'dark';

      if (userThemeSetting === 'system') {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    }

    mediaQuery.addEventListener('change', handleThemeChange);

    return () => {
      mediaQuery.removeEventListener('change', handleThemeChange);
    };
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme }}>{children}</ThemeContext.Provider>
  );
}
