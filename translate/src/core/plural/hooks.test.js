import { usePluralForm, useTranslationForEntity } from './hooks';

import sinon from 'sinon';
import * as Hooks from '~/hooks';

beforeAll(() => {
  sinon.stub(Hooks, 'useAppSelector');
});
afterAll(() => {
  Hooks.useAppSelector.restore();
});

const fakeSelector = (pluralForm) => (cb) => cb({ plural: { pluralForm } });

describe('usePluralForm', () => {
  it('returns the plural form', () => {
    Hooks.useAppSelector.callsFake(fakeSelector(3));
    expect(usePluralForm(undefined)).toEqual(3);

    Hooks.useAppSelector.callsFake(fakeSelector(-1));
    expect(usePluralForm(undefined)).toEqual(-1);

    Hooks.useAppSelector.callsFake(fakeSelector(-1));
    expect(usePluralForm({ original_plural: '' })).toEqual(-1);
  });

  it('corrects the plural number', () => {
    Hooks.useAppSelector.callsFake(fakeSelector(-1));
    expect(usePluralForm({ original_plural: 'I have a plural!' })).toEqual(0);
  });
});

describe('useTranslationForEntity', () => {
  it('returns the correct string', () => {
    Hooks.useAppSelector.callsFake(fakeSelector(-1));
    const res = useTranslationForEntity({ translation: [{ string: 'world' }] });
    expect(res).toEqual({ string: 'world' });
  });

  it('does not return rejected translations', () => {
    Hooks.useAppSelector.callsFake(fakeSelector(-1));
    const res = useTranslationForEntity({
      translation: [{ string: 'wat', rejected: true }],
    });
    expect(res).toBeUndefined();
  });
});
