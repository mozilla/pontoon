export function useTheme() {
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

  return function useTheme(newTheme: string) {
    if (newTheme === 'system') {
      newTheme = getSystemTheme();
      storeSystemTheme(newTheme);
    }
    document.body.classList.remove('dark-theme', 'light-theme', 'system-theme');
    document.body.classList.add(`${newTheme}-theme`);
  };
}
