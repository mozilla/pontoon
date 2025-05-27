import { createContext, useEffect, useState } from 'react';
import { useTheme } from '~/hooks/useTheme';

export const ThemeContext = createContext({
  theme: 'dark',
});

export function ThemeProvider({ children }: { children: React.ReactElement }) {
  const [theme] = useState(
    () => document.body.getAttribute('data-theme') || 'system',
  );

  const applyTheme = useTheme();

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    function handleThemeChange() {
      let userThemeSetting = document.body.getAttribute('data-theme');

      if (userThemeSetting === 'system') {
        applyTheme(userThemeSetting);
      }
    }

    mediaQuery.addEventListener('change', handleThemeChange);

    if (theme === 'system') {
      applyTheme(theme);
    }

    return () => {
      mediaQuery.removeEventListener('change', handleThemeChange);
    };
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme }}>{children}</ThemeContext.Provider>
  );
}
