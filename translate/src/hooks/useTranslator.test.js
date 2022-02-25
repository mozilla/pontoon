import sinon from 'sinon';

import { NAME as LOCALE } from '~/core/locale';
import { NAME as PROJECT } from '~/core/project';
import { NAME as USER } from '~/core/user';
import * as hookModule from '~/hooks';
import { useTranslator } from './useTranslator';

beforeAll(() => sinon.stub(hookModule, 'useAppSelector'));
afterAll(() => hookModule.useAppSelector.restore());

const fakeSelector = (user) => (sel) =>
  sel({
    [LOCALE]: { code: 'mylocale' },
    [PROJECT]: { slug: 'myproject' },
    [USER]: user,
  });

describe('useTranslator', () => {
  it('returns false for non-authenticated users', () => {
    hookModule.useAppSelector.callsFake(
      fakeSelector({ isAuthenticated: false }),
    ),
      expect(useTranslator()).toBeFalsy();
  });

  it('returns true if user is a manager of the locale', () => {
    hookModule.useAppSelector.callsFake(
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
    hookModule.useAppSelector.callsFake(
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
    hookModule.useAppSelector.callsFake(
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
