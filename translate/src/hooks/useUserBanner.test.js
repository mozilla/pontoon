import React from 'react';

import { USER } from '~/modules/user';
import * as Hooks from '~/hooks';

import { useUserBanner } from './useUserBanner';
import { vi } from 'vitest';

beforeAll(() => {
  vi.mock('react', async (importOriginal) => {
    const actual = await importOriginal();
    return {
      ...actual,
      useContext: () => ({ code: 'mylocale', project: 'myproject' }),
    };
  });
  vi.spyOn(Hooks, 'useAppSelector');
});

afterAll(() => {
  vi.restoreAllMocks();
});

const fakeSelector = (user) => (sel) =>
  sel({
    [USER]: user,
  });

describe('useUserBanner', () => {
  it('returns empty parameters for non-authenticated users', () => {
    (Hooks.useAppSelector.mockImplementation(
      fakeSelector({ isAuthenticated: false }),
    ),
      expect(useUserBanner()).toStrictEqual(['', '']));
  });

  it('returns [ADMIN, Admin] if user has admin permissions', () => {
    Hooks.useAppSelector.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        isAdmin: true,
        pmForProjects: [],
        managerForLocales: [],
        translatorForLocales: [],
      }),
    );
    expect(useUserBanner()).toStrictEqual(['ADMIN', 'Admin']);
  });

  it('returns [PM, Project Manager] if user is a project manager for the project', () => {
    Hooks.useAppSelector.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: ['myproject'],
        managerForLocales: [],
        translatorForLocales: [],
      }),
    );
    expect(useUserBanner()).toStrictEqual(['PM', 'Project Manager']);
  });

  it('returns [PM, Project Manager] if user is a project manager for the project, even if user is an Admin', () => {
    Hooks.useAppSelector.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        isAdmin: true,
        pmForProjects: ['myproject'],
        managerForLocales: [],
        translatorForLocales: [],
      }),
    );
    expect(useUserBanner()).toStrictEqual(['PM', 'Project Manager']);
  });

  it('returns [MNGR, Manager] if user is a manager of the locale', () => {
    Hooks.useAppSelector.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: [],
        managerForLocales: ['mylocale'],
        translatorForLocales: [],
      }),
    );
    expect(useUserBanner()).toStrictEqual(['MNGR', 'Team Manager']);
  });

  it('returns [MNGR, Manager] if user is a manager of the locale, even if user is an Admin', () => {
    Hooks.useAppSelector.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        isAdmin: true,
        pmForProjects: [],
        managerForLocales: ['mylocale'],
        translatorForLocales: [],
      }),
    );
    expect(useUserBanner()).toStrictEqual(['MNGR', 'Team Manager']);
  });

  it('returns [MNGR, Manager] if user is a manager of the locale, even if user is a Project Manager', () => {
    Hooks.useAppSelector.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: ['myproject'],
        managerForLocales: ['mylocale'],
        translatorForLocales: [],
      }),
    );
    expect(useUserBanner()).toStrictEqual(['MNGR', 'Team Manager']);
  });

  it('returns [TRNSL, Translator] if user is a translator for the locale', () => {
    Hooks.useAppSelector.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: [],
        managerForLocales: [],
        translatorForLocales: ['mylocale'],
      }),
    );
    expect(useUserBanner()).toStrictEqual(['TRNSL', 'Translator']);
  });

  it('returns [NEW, New User] if user created their account within the last 3 months', () => {
    const dateJoined = new Date();
    dateJoined.setMonth(dateJoined.getMonth() - 2);
    Hooks.useAppSelector.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: [],
        managerForLocales: [],
        translatorForLocales: [],
        dateJoined: dateJoined,
      }),
    );
    expect(useUserBanner()).toStrictEqual(['NEW', 'New User']);

    // Set join date to be 6 months ago (no longer a new user)
    dateJoined.setMonth(dateJoined.getMonth() - 6);
    Hooks.useAppSelector.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: [],
        managerForLocales: [],
        translatorForLocales: [],
        dateJoined: dateJoined,
      }),
    );
    expect(useUserBanner()).toStrictEqual(['', '']);
  });
});
