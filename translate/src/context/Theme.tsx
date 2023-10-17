import { createContext, useEffect, useState } from 'react';

export const ThemeContext = createContext({
  theme: 'system',
});

function getSystemTheme() {
  if (
    window.matchMedia &&
    window.matchMedia('(prefers-color-scheme: dark)').matches
  ) {
    return 'dark';
  } else {
    return 'light';
  }
}

export function ThemeProvider({ children }: { children: React.ReactElement }) {
  const [theme] = useState(() => document.body.getAttribute('data-theme')!);

  useEffect(() => {
    function applyTheme(newTheme: string) {
      if (newTheme === 'system') {
        newTheme = getSystemTheme();
      }
      document.body.classList.remove(
        'dark-theme',
        'light-theme',
        'system-theme',
      );
      document.body.classList.add(`${newTheme}-theme`);
    }

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    function handleThemeChange(e: MediaQueryListEvent) {
      let userThemeSetting = document.body.getAttribute('data-theme')!;

      if (userThemeSetting === 'system') {
        if (e.matches) {
          applyTheme('dark');
        } else {
          applyTheme('light');
        }
      } else {
        applyTheme(userThemeSetting);
      }
    }

    mediaQuery.addEventListener('change', handleThemeChange);
    if (document.body.classList.contains('system-theme')) {
      let systemTheme = getSystemTheme();
      document.body.classList.remove('system-theme');
      document.body.classList.add(`${systemTheme}-theme`);
    } else {
      applyTheme(document.body.getAttribute('data-theme')!);
    }

    return () => {
      mediaQuery.removeEventListener('change', handleThemeChange);
    };
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme }}>{children}</ThemeContext.Provider>
  );
}
