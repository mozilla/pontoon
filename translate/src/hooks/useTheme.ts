export function useTheme() {
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

  function applyTheme(newTheme: string) {
    if (newTheme === 'system') {
      newTheme = getSystemTheme();
    }
    document.body.classList.remove('dark-theme', 'light-theme', 'system-theme');
    document.body.classList.add(`${newTheme}-theme`);
  }

  return { applyTheme };
}
