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
  const [theme, setTheme] = useState(() => {
    const currentTheme = document.body.getAttribute('data-theme') || 'system';
    if (currentTheme === 'system') {
      return getSystemTheme();
    }
    return currentTheme;
  });

  useEffect(() => {
    function applyTheme(newTheme: string) {
      if (newTheme === 'system') {
        newTheme = getSystemTheme();
      }
      document.body.classList.remove('dark-theme', 'light-theme');
      document.body.classList.add(`${newTheme}-theme`);
    }

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    function handleThemeChange(e: MediaQueryListEvent) {
      let userThemeSetting =
        document.body.getAttribute('data-theme') || 'system';

      if (userThemeSetting === 'system') {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    }

    mediaQuery.addEventListener('change', handleThemeChange);

    applyTheme(theme);

    return () => {
      mediaQuery.removeEventListener('change', handleThemeChange);
    };
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme }}>
      {children}
    </ThemeContext.Provider>
  );
}
