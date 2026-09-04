import { vi } from 'vitest';

import { useTheme } from './useTheme';

describe('useTheme', () => {
  it('sets the body class and dispatches a themechange event', () => {
    const onThemeChange = vi.fn();
    document.addEventListener('themechange', onThemeChange);

    useTheme()('light');

    expect(document.body.classList.contains('light-theme')).toBe(true);
    expect(onThemeChange).toHaveBeenCalledTimes(1);
    expect(onThemeChange.mock.calls[0][0].detail).toEqual({ theme: 'light' });

    document.removeEventListener('themechange', onThemeChange);
  });
});
