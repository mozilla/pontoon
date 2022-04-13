import React from 'react';
import sinon from 'sinon';

import { usePluralForm, useTranslationForEntity } from './pluralForm';

beforeAll(() => sinon.stub(React, 'useContext'));
afterAll(() => React.useContext.restore());

describe('usePluralForm', () => {
  it('returns the plural form', () => {
    React.useContext.returns({ pluralForm: 3 });
    expect(usePluralForm(undefined)).toEqual({ pluralForm: 3 });

    React.useContext.returns({ pluralForm: -1 });
    expect(usePluralForm(undefined)).toEqual({ pluralForm: -1 });

    React.useContext.returns({ pluralForm: -1 });
    expect(usePluralForm({ original_plural: '' })).toEqual({ pluralForm: -1 });
  });

  it('corrects the plural number', () => {
    React.useContext.returns({ pluralForm: -1 });
    expect(usePluralForm({ original_plural: 'I have a plural!' })).toEqual({
      pluralForm: 0,
    });
  });
});

describe('useTranslationForEntity', () => {
  it('returns the correct string', () => {
    React.useContext.returns({ pluralForm: -1 });
    const res = useTranslationForEntity({ translation: [{ string: 'world' }] });
    expect(res).toEqual({ string: 'world' });
  });

  it('does not return rejected translations', () => {
    React.useContext.returns({ pluralForm: -1 });
    const res = useTranslationForEntity({
      translation: [{ string: 'wat', rejected: true }],
    });
    expect(res).toBeUndefined();
  });
});
