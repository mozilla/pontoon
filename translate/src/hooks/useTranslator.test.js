import React from 'react';
import { PROJECT } from '~/modules/project';
import { USER } from '~/modules/user';
import * as Hooks from '~/hooks';

import { useTranslator } from './useTranslator';
import { vi } from 'vitest';

beforeAll(() => {
  vi.spyOn(Hooks, 'useAppSelector');
  vi.mock('react', async (importOriginal) => {
    const actual = await importOriginal();
    return {
      ...actual,
      useContext: () => ({ code: 'mylocale' }),
    };
  });
});

afterAll(() => {
  vi.restoreAllMocks();
});

const fakeSelector = (user) => (sel) =>
  sel({
    [PROJECT]: { slug: 'myproject' },
    [USER]: user,
  });

describe('useTranslator', () => {
  it('returns false for non-authenticated users', () => {
    Hooks.useAppSelector.mockImplementation(
      fakeSelector({ isAuthenticated: false }),
    );
    expect(useTranslator()).toBeFalsy();
  });

  it('returns true if user is a manager of the locale', () => {
    Hooks.useAppSelector.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        canManageLocales: ['mylocale'],
        canTranslateLocales: [],
        translatorForProjects: {},
      }),
    );
    expect(useTranslator()).toBeTruthy();
  });

  it('returns true if user is a translator of the locale', () => {
    Hooks.useAppSelector.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        canManageLocales: [],
        canTranslateLocales: ['mylocale'],
        translatorForProjects: {},
      }),
    );
    expect(useTranslator()).toBeTruthy();
  });

  it('returns true if user is a translator for project-locale', () => {
    Hooks.useAppSelector.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        canManageLocales: ['localeA'],
        canTranslateLocales: ['localeB'],
        translatorForProjects: { 'mylocale-myproject': true },
      }),
    );
    expect(useTranslator()).toBeTruthy();
  });
});
