import React from 'react';
import sinon from 'sinon';

import { USER } from '~/modules/user';
import * as Hooks from '~/hooks';

import { useUserStatus } from './useUserStatus';

beforeAll(() => {
  sinon.stub(Hooks, 'useAppSelector');
  sinon
    .stub(React, 'useContext')
    .returns({ code: 'mylocale', project: 'myproject' });
});
afterAll(() => {
  Hooks.useAppSelector.restore();
  React.useContext.restore();
});

const fakeSelector = (user) => (sel) =>
  sel({
    [USER]: user,
  });

describe('useUserStatus', () => {
  it('returns empty parameters for non-authenticated users', () => {
    Hooks.useAppSelector.callsFake(fakeSelector({ isAuthenticated: false })),
      expect(useUserStatus()).toStrictEqual(['', '']);
  });

  it('returns [ADMIN, Admin] if user has admin permissions', () => {
    Hooks.useAppSelector.callsFake(
      fakeSelector({
        isAuthenticated: true,
        isAdmin: true,
        pmForProjects: [],
        managerForLocales: [],
        translatorForLocales: [],
      }),
    );
    expect(useUserStatus()).toStrictEqual(['ADMIN', 'Admin']);
  });

  it('returns [PM, Project Manager] if user is a project manager for the project', () => {
    Hooks.useAppSelector.callsFake(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: ['myproject'],
        managerForLocales: [],
        translatorForLocales: [],
      }),
    );
    expect(useUserStatus()).toStrictEqual(['PM', 'Project Manager']);
  });

  it('returns [PM, Project Manager] if user is a project manager for the project, even if user is an Admin', () => {
    Hooks.useAppSelector.callsFake(
      fakeSelector({
        isAuthenticated: true,
        isAdmin: true,
        pmForProjects: ['myproject'],
        managerForLocales: [],
        translatorForLocales: [],
      }),
    );
    expect(useUserStatus()).toStrictEqual(['PM', 'Project Manager']);
  });

  it('returns [MNGR, Manager] if user is a manager of the locale', () => {
    Hooks.useAppSelector.callsFake(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: [],
        managerForLocales: ['mylocale'],
        translatorForLocales: [],
      }),
    );
    expect(useUserStatus()).toStrictEqual(['MNGR', 'Team Manager']);
  });

  it('returns [MNGR, Manager] if user is a manager of the locale, even if user is an Admin', () => {
    Hooks.useAppSelector.callsFake(
      fakeSelector({
        isAuthenticated: true,
        isAdmin: true,
        pmForProjects: [],
        managerForLocales: ['mylocale'],
        translatorForLocales: [],
      }),
    );
    expect(useUserStatus()).toStrictEqual(['MNGR', 'Team Manager']);
  });

  it('returns [MNGR, Manager] if user is a manager of the locale, even if user is a Project Manager', () => {
    Hooks.useAppSelector.callsFake(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: ['myproject'],
        managerForLocales: ['mylocale'],
        translatorForLocales: [],
      }),
    );
    expect(useUserStatus()).toStrictEqual(['MNGR', 'Team Manager']);
  });

  it('returns [TRNSL, Translator] if user is a translator for the locale', () => {
    Hooks.useAppSelector.callsFake(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: [],
        managerForLocales: [],
        translatorForLocales: ['mylocale'],
      }),
    );
    expect(useUserStatus()).toStrictEqual(['TRNSL', 'Translator']);
  });

  it('returns [NEW, New User] if user created their account within the last 3 months', () => {
    const dateJoined = new Date();
    dateJoined.setMonth(dateJoined.getMonth() - 2);
    Hooks.useAppSelector.callsFake(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: [],
        managerForLocales: [],
        translatorForLocales: [],
        dateJoined: dateJoined,
      }),
    );
    expect(useUserStatus()).toStrictEqual(['NEW', 'New User']);

    // Set join date to be 6 months ago (no longer a new user)
    dateJoined.setMonth(dateJoined.getMonth() - 6);
    Hooks.useAppSelector.callsFake(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: [],
        managerForLocales: [],
        translatorForLocales: [],
        dateJoined: dateJoined,
      }),
    );
    expect(useUserStatus()).toStrictEqual(['', '']);
  });
});
