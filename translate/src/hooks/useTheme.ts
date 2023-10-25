import { useEffect } from 'react';

function getSystemTheme(): string {
  if (
    window.matchMedia &&
    window.matchMedia('(prefers-color-scheme: dark)').matches
  ) {
    return 'dark';
  } else {
    return 'light';
  }
}

export function useTheme(initialTheme: string) {
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
      let userThemeSetting = document.body.getAttribute('data-theme') || 'dark';

      if (userThemeSetting === 'system') {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    }

    mediaQuery.addEventListener('change', handleThemeChange);

    applyTheme(initialTheme);

    return () => {
      mediaQuery.removeEventListener('change', handleThemeChange);
    };
  }, [initialTheme]);
}
