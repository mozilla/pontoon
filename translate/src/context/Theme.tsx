import { createContext, useEffect, useState } from 'react';
import { useTheme } from '~/hooks/useTheme';

export const ThemeContext = createContext({
  theme: 'dark',
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

/*
 * Storing system theme setting in a cookie makes the setting available to the server.
 * That allows us to set the theme class already in the Django template, which (unlike
 * setting it on the client) prevents FOUC.
 */
function storeSystemTheme(systemTheme: string) {
  document.cookie = `system_theme=${systemTheme}; path=/; max-age=${
    60 * 60 * 24 * 365
  }; Secure`;
}

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
        const systemTheme = e.matches ? 'dark' : 'light';
        applyTheme(systemTheme);
        storeSystemTheme(systemTheme);
      }
    }

    mediaQuery.addEventListener('change', handleThemeChange);

    if (theme == 'system') {
      applyTheme(theme);
      storeSystemTheme(getSystemTheme());
    }

    return () => {
      mediaQuery.removeEventListener('change', handleThemeChange);
    };
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme }}>{children}</ThemeContext.Provider>
  );
}
