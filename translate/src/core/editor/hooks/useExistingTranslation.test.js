import React from 'react';
import sinon from 'sinon';
import * as PluralForm from '~/context/PluralForm';
import { parseEntry } from '~/core/utils/fluent/parser';
import * as Hooks from '~/hooks';
import * as SelectedEntity from '~/core/entities/hooks';

import { useExistingTranslation } from './useExistingTranslation';

const ACTIVE_TRANSLATION = { pk: 1 };

const HISTORY_STRING = {
  translations: [
    { pk: 12, string: 'I was there before' },
    { pk: 98, string: 'hello, world!' },
    { pk: 10010, string: '' },
  ],
};

const HISTORY_FLUENT = {
  translations: [
    { pk: 12, string: 'msg = I like { -brand }' },
    { pk: 98, string: 'msg = hello, world!' },
    { pk: 431, string: 'msg = Come on Morty!\n' },
  ],
};

const ENTITY_STRING = { format: 'po' };
const ENTITY_FLUENT = { format: 'ftl', original: 'msg = Allez Morty !' };

beforeAll(() => {
  sinon.stub(React, 'useContext');
  sinon.stub(Hooks, 'useAppSelector');
  sinon.stub(SelectedEntity, 'useSelectedEntity');
  sinon.stub(PluralForm, 'useTranslationForEntity');
});
beforeEach(() => {
  Hooks.useAppSelector.callsFake((cb) => cb({ history: HISTORY_STRING }));
  SelectedEntity.useSelectedEntity.returns(ENTITY_STRING);
  PluralForm.useTranslationForEntity.returns(ACTIVE_TRANSLATION);
});
afterAll(() => {
  React.useContext.restore();
  Hooks.useAppSelector.restore();
  SelectedEntity.useSelectedEntity.restore();
  PluralForm.useTranslationForEntity.restore();
});

describe('useExistingTranslation', () => {
  it('finds identical initial/active translation', () => {
    React.useContext.returns({
      format: 'simple',
      initial: 'something',
      value: 'something',
    });

    expect(useExistingTranslation()).toBe(ACTIVE_TRANSLATION);
  });

  it('finds identical Fluent initial/active translation', () => {
    SelectedEntity.useSelectedEntity.returns(ENTITY_FLUENT);
    React.useContext.returns({
      format: 'ftl',
      initial: 'msg = something',
      value: parseEntry('msg = something'),
    });

    expect(useExistingTranslation()).toBe(ACTIVE_TRANSLATION);
  });

  it('finds empty initial/active translation', () => {
    React.useContext.returns({ format: 'simple', initial: '', value: '' });

    expect(useExistingTranslation()).toBe(ACTIVE_TRANSLATION);
  });

  it('finds identical translation in history', () => {
    const prev0 = HISTORY_STRING.translations[0];
    React.useContext.returns({
      format: 'simple',
      initial: '',
      value: prev0.string,
    });

    expect(useExistingTranslation()).toBe(prev0);

    const prev1 = HISTORY_STRING.translations[1];
    React.useContext.returns({
      format: 'simple',
      initial: '',
      value: prev1.string,
    });

    expect(useExistingTranslation()).toBe(prev1);
  });

  it('finds identical Fluent translation in history', () => {
    Hooks.useAppSelector.callsFake((cb) => cb({ history: HISTORY_FLUENT }));
    SelectedEntity.useSelectedEntity.returns(ENTITY_FLUENT);

    const prev0 = HISTORY_FLUENT.translations[0];
    React.useContext.returns({
      format: 'ftl',
      initial: 'msg = something',
      value: parseEntry(prev0.string),
    });

    expect(useExistingTranslation()).toBe(prev0);

    const prev1 = HISTORY_FLUENT.translations[1];
    React.useContext.returns({
      format: 'ftl',
      initial: 'msg = something',
      value: parseEntry(prev1.string),
    });

    expect(useExistingTranslation()).toBe(prev1);
  });

  it('finds empty translation in history', () => {
    React.useContext.returns({ format: 'simple', initial: 'x', value: '' });

    expect(useExistingTranslation()).toBe(HISTORY_STRING.translations[2]);
  });

  it('finds a Fluent translation in history from a simplified Fluent string', () => {
    Hooks.useAppSelector.callsFake((cb) => cb({ history: HISTORY_FLUENT }));
    SelectedEntity.useSelectedEntity.returns(ENTITY_FLUENT);
    React.useContext.returns({
      format: 'ftl',
      initial: 'msg = something',
      value: 'Come on Morty!',
      view: 'simple',
    });

    expect(useExistingTranslation()).toBe(HISTORY_FLUENT.translations[2]);
  });
});
