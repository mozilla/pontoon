import React from 'react';
import sinon from 'sinon';

import { PROJECT } from '../../src/modules/project';
import { USER } from '../../src/modules/user';
import * as Hooks from '../../src/hooks';

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
    (Hooks.useAppSelector.callsFake(fakeSelector({ isAuthenticated: false })),
      expect(useTranslator()).toBeFalsy());
  });

  it('returns true if user is a manager of the locale', () => {
    Hooks.useAppSelector.callsFake(
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
    Hooks.useAppSelector.callsFake(
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
    Hooks.useAppSelector.callsFake(
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
