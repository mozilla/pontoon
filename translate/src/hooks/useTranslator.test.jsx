import React from 'react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import { renderHook } from '@testing-library/react-hooks';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

import { useTranslator } from './useTranslator';

// Import real context + constants
import { Locale } from '~/context/Locale';
import { USER } from '~/modules/user';

// Mock `useProject` hook
vi.mock('~/modules/project', () => ({
  useProject: vi.fn(),
}));
import { useProject } from '~/modules/project';

// Create wrapper for renderHook
const makeWrapper = (userState, { locale = 'mylocale', project = 'myproject' } = {}) => {
  return ({ children }) => {
    const store = configureStore({
      reducer: (state) => state,
      preloadedState: { [USER]: userState },
    });

    useProject.mockReturnValue({ slug: project });

    return (
      <Provider store={store}>
        <Locale.Provider value={{ code: locale }}>{children}</Locale.Provider>
      </Provider>
    );
  };
};

afterEach(() => {
  vi.clearAllMocks();
});

describe('useTranslator', () => {
  it('returns false for non-authenticated users', () => {
    const wrapper = makeWrapper({ isAuthenticated: false });
    const { result } = renderHook(() => useTranslator(), { wrapper });
    expect(result.current).toBe(false);
  });

  it('returns true if user is a manager of the locale', () => {
    const wrapper = makeWrapper({
      isAuthenticated: true,
      canManageLocales: ['mylocale'],
      canTranslateLocales: [],
      translatorForProjects: {},
    });
    const { result } = renderHook(() => useTranslator(), { wrapper });
    expect(result.current).toBe(true);
  });

  it('returns true if user is a translator of the locale', () => {
    const wrapper = makeWrapper({
      isAuthenticated: true,
      canManageLocales: [],
      canTranslateLocales: ['mylocale'],
      translatorForProjects: {},
    });
    const { result } = renderHook(() => useTranslator(), { wrapper });
    expect(result.current).toBe(true);
  });

  it('returns true if user is a translator for project-locale', () => {
    const wrapper = makeWrapper(
      {
        isAuthenticated: true,
        canManageLocales: ['localeA'],
        canTranslateLocales: ['localeB'],
        translatorForProjects: { 'mylocale-myproject': true },
      },
      { locale: 'mylocale', project: 'myproject' }
    );
    const { result } = renderHook(() => useTranslator(), { wrapper });
    expect(result.current).toBe(true);
  });
});
