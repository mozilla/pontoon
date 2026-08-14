import { PROJECT } from '~/modules/project';
import { USER } from '~/modules/user';
import * as Hooks from '~/hooks';

import { useTranslator } from './useTranslator';
import { vi } from 'vitest';

vi.spyOn(Hooks, 'useAppSelector');

const ctx = vi.hoisted(() => ({ code: 'mylocale', entity: { project: {} } }));
vi.mock('react', async (importOriginal) => {
  const actual = await importOriginal();
  return { ...actual, useContext: () => ctx };
});

beforeEach(() => {
  ctx.entity = { project: {} };
});

afterAll(() => {
  vi.restoreAllMocks();
});

const fakeSelector =
  (user, slug = 'myproject') =>
  (sel) =>
    sel({
      [PROJECT]: { slug },
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

  it('returns true for a project the user translates, in the All Projects view', () => {
    ctx.entity = { project: { slug: 'myproject' } };
    Hooks.useAppSelector.mockImplementation(
      fakeSelector(
        {
          isAuthenticated: true,
          canManageLocales: [],
          canTranslateLocales: [],
          translatorForProjects: { 'mylocale-myproject': true },
        },
        'all-projects',
      ),
    );
    expect(useTranslator()).toBeTruthy();
  });

  it('uses the given entity rather than the selected one', () => {
    ctx.entity = { project: { slug: 'myproject' } };
    Hooks.useAppSelector.mockImplementation(
      fakeSelector(
        {
          isAuthenticated: true,
          canManageLocales: [],
          canTranslateLocales: [],
          translatorForProjects: { 'mylocale-myproject': true },
        },
        'all-projects',
      ),
    );
    expect(useTranslator({ project: { slug: 'otherproject' } })).toBeFalsy();
  });

  it('falls back to the locale permission with no string in hand', () => {
    Hooks.useAppSelector.mockImplementation(
      fakeSelector(
        {
          isAuthenticated: true,
          canManageLocales: [],
          canTranslateLocales: ['mylocale'],
          translatorForProjects: { 'mylocale-myproject': false },
        },
        'all-projects',
      ),
    );
    expect(useTranslator()).toBeTruthy();
  });
});
