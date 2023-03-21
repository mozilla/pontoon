import React from 'react';
import sinon from 'sinon';

import { PROJECT } from '~/modules/project';
import { USER } from '~/modules/user';
import * as Hooks from '~/hooks';

import { useTranslator } from './useTranslator';

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
    [PROJECT]: { slug: 'myproject' },
    [USER]: user,
  });

describe('useTranslator', () => {
  it('returns false for non-authenticated users', () => {
    Hooks.useAppSelector.callsFake(fakeSelector({ isAuthenticated: false })),
      expect(useTranslator()).toBeFalsy();
  });

  it('returns true if user is a manager of the locale', () => {
    Hooks.useAppSelector.callsFake(
      fakeSelector({
        isAuthenticated: true,
        managerForLocales: ['mylocale'],
        translatorForLocales: [],
        translatorForProjects: {},
      }),
    );
    expect(useTranslator()).toBeTruthy();
  });

  it('returns true if user is a translator of the locale', () => {
    Hooks.useAppSelector.callsFake(
      fakeSelector({
        isAuthenticated: true,
        managerForLocales: [],
        translatorForLocales: ['mylocale'],
        translatorForProjects: {},
      }),
    );
    expect(useTranslator()).toBeTruthy();
  });

  it('returns true if user is a translator for project-locale', () => {
    Hooks.useAppSelector.callsFake(
      fakeSelector({
        isAuthenticated: true,
        managerForLocales: ['localeA'],
        translatorForLocales: ['localeB'],
        translatorForProjects: { 'mylocale-myproject': true },
      }),
    );
    expect(useTranslator()).toBeTruthy();
  });
});
