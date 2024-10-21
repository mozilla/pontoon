import React from 'react';
import sinon from 'sinon';

import { USER } from '~/modules/user';
import * as Hooks from '~/hooks';

import { useUserStatus } from './useUserStatus';

beforeAll(() => {
  sinon.stub(Hooks, 'useAppSelector');
  sinon.stub(React, 'useContext').returns({ code: 'mylocale' });
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
        managerForLocales: [],
        translatorForLocales: [],
      }),
    );
    expect(useUserStatus()).toStrictEqual(['ADMIN', 'Admin']);
  });

  it('returns [MNGR, Manager] if user is a manager of the locale', () => {
    Hooks.useAppSelector.callsFake(
      fakeSelector({
        isAuthenticated: true,
        managerForLocales: ['mylocale'],
        translatorForLocales: [],
      }),
    );
    expect(useUserStatus()).toStrictEqual(['MNGR', 'Manager']);
  });

  it('returns [TRNSL, Translator] if user is a translator for the locale', () => {
    Hooks.useAppSelector.callsFake(
      fakeSelector({
        isAuthenticated: true,
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
        managerForLocales: [],
        translatorForLocales: [],
        dateJoined: dateJoined,
      }),
    );
    expect(useUserStatus()).toStrictEqual(['', '']);
  });
});
