import sinon from 'sinon';
import * as PluralForm from '~/context/pluralForm';
import { parser as fluentParser } from '~/core/utils/fluent/parser';
import { flattenMessage } from '~/core/utils/fluent/flattenMessage';
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

const stringSelector =
  ({ initialTranslation = 'something', translation }) =>
  (cb) =>
    cb({
      editor: { initialTranslation, translation },
      history: HISTORY_STRING,
    });

const fluentSelector =
  ({
    initialTranslation = fluentParser.parseEntry('msg = something'),
    translation,
  }) =>
  (cb) =>
    cb({
      editor: { initialTranslation, translation },
      history: HISTORY_FLUENT,
    });

beforeAll(() => {
  sinon.stub(Hooks, 'useAppSelector');
  sinon.stub(SelectedEntity, 'useSelectedEntity');
  sinon.stub(PluralForm, 'useTranslationForEntity');
});
beforeEach(() => {
  PluralForm.useTranslationForEntity.returns(ACTIVE_TRANSLATION);
  SelectedEntity.useSelectedEntity.returns(ENTITY_STRING);
});
afterAll(() => {
  Hooks.useAppSelector.restore();
  SelectedEntity.useSelectedEntity.restore();
  PluralForm.useTranslationForEntity.restore();
});

describe('useExistingTranslation', () => {
  it('finds identical initial/active translation', () => {
    Hooks.useAppSelector.callsFake(
      stringSelector({
        initialTranslation: 'something',
        translation: 'something',
      }),
    );
    expect(useExistingTranslation()).toBe(ACTIVE_TRANSLATION);
  });

  it('finds identical Fluent initial/active translation', () => {
    SelectedEntity.useSelectedEntity.returns(ENTITY_FLUENT);
    Hooks.useAppSelector.callsFake(
      fluentSelector({
        translation: fluentParser.parseEntry('msg = something'),
      }),
    );
    expect(useExistingTranslation()).toBe(ACTIVE_TRANSLATION);
  });

  it('finds empty initial/active translation', () => {
    Hooks.useAppSelector.callsFake(
      stringSelector({ initialTranslation: '', translation: '' }),
    );
    expect(useExistingTranslation()).toBe(ACTIVE_TRANSLATION);
  });

  it('finds identical translation in history', () => {
    const prev0 = HISTORY_STRING.translations[0];
    Hooks.useAppSelector.callsFake(
      stringSelector({ translation: prev0.string }),
    );
    expect(useExistingTranslation()).toBe(prev0);

    const prev1 = HISTORY_STRING.translations[1];
    Hooks.useAppSelector.callsFake(
      stringSelector({ translation: prev1.string }),
    );
    expect(useExistingTranslation()).toBe(prev1);
  });

  it('finds identical Fluent translation in history', () => {
    SelectedEntity.useSelectedEntity.returns(ENTITY_FLUENT);

    const prev0 = HISTORY_FLUENT.translations[0];
    Hooks.useAppSelector.callsFake(
      fluentSelector({
        translation: flattenMessage(fluentParser.parseEntry(prev0.string)),
      }),
    );
    expect(useExistingTranslation()).toBe(prev0);

    const prev1 = HISTORY_FLUENT.translations[1];
    Hooks.useAppSelector.callsFake(
      fluentSelector({
        translation: flattenMessage(fluentParser.parseEntry(prev1.string)),
      }),
    );
    expect(useExistingTranslation()).toBe(prev1);
  });

  it('finds empty translation in history', () => {
    Hooks.useAppSelector.callsFake(stringSelector({ translation: '' }));
    expect(useExistingTranslation()).toBe(HISTORY_STRING.translations[2]);
  });

  it('finds a Fluent translation in history from a simplified Fluent string', () => {
    SelectedEntity.useSelectedEntity.returns(ENTITY_FLUENT);
    Hooks.useAppSelector.callsFake(
      fluentSelector({ initialTranslation: '', translation: 'Come on Morty!' }),
    );
    expect(useExistingTranslation()).toBe(HISTORY_FLUENT.translations[2]);
  });
});
