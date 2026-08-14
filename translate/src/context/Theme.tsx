import { createContext, useCallback, useEffect, useState } from 'react';
import { updateUserEditorTheme } from '~/api/user';
import { useTheme } from '~/hooks/useTheme';

type ThemeContextType = {
  theme: string;
  editorTheme: string;
  setEditorTheme: (editorTheme: string) => void;
};

export function editorThemeClass(editorTheme: string | null): string {
  return editorTheme === 'dark' || editorTheme === 'light'
    ? `${editorTheme}-theme`
    : '';
}

export const ThemeContext = createContext<ThemeContextType>({
  theme: 'dark',
  editorTheme: 'match',
  setEditorTheme: () => {},
});

export function ThemeProvider({ children }: { children: React.ReactElement }) {
  const [theme] = useState(
    () => document.body.getAttribute('data-theme') || 'system',
  );
  const [editorTheme, setEditorThemeState] = useState(
    () => document.body.getAttribute('data-editor-theme') || 'light',
  );

  const setEditorTheme = useCallback((newEditorTheme: string) => {
    setEditorThemeState(newEditorTheme);
    document.body.setAttribute('data-editor-theme', newEditorTheme);
    updateUserEditorTheme(newEditorTheme);
  }, []);

  const applyTheme = useTheme();

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    function handleThemeChange() {
      const userThemeSetting = document.body.getAttribute('data-theme');

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
    <ThemeContext.Provider value={{ theme, editorTheme, setEditorTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
