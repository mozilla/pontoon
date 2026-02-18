import React from 'react';

import { EditorActions } from '~/context/Editor';
import { HelperSelection } from '~/context/HelperSelection';
import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';

import { OtherLocaleTranslationComponent } from './OtherLocaleTranslation';
import { vi } from 'vitest';
import { fireEvent } from '@testing-library/react';

const LOCALE = { code: 'fr-FR', name: 'French', direction: 'ltr', script: '' };
const PLAIN_TRANSLATION = {
  translation: 'Un cheval, un cheval ! Mon royaume pour un cheval !',
  locale: LOCALE,
};
const FLUENT_TRANSLATION = {
  translation: 'key = Un cheval, un cheval ! Mon royaume pour un cheval !',
  locale: LOCALE,
};
const MF2_TRANSLATION = {
  translation: '{{Un cheval, un cheval ! Mon royaume pour un cheval !}}',
  locale: LOCALE,
};

function createTranslation(format, translation, setEditorFromHelpers) {
  const store = createReduxStore();
  const Wrapper = (props) => (
    <EditorActions.Provider value={{ setEditorFromHelpers }}>
      <HelperSelection.Provider value={{ element: -1, setElement() {} }}>
        <OtherLocaleTranslationComponent {...props} />
      </HelperSelection.Provider>
    </EditorActions.Provider>
  );
  const wrapper = mountComponentWithStore(Wrapper, store, {
    entity: { format },
    parameters: { project: 'p', resource: 'r', entity: 'e' },
    translation,
  });
  createDefaultUser(store);
  return wrapper;
}

describe('<OtherLocaleTranslationComponent>', () => {
  let getSelectionBackup;

  beforeAll(() => {
    getSelectionBackup = window.getSelection;
    window.getSelection = () => {
      return {
        toString: () => {},
      };
    };
  });

  afterAll(() => {
    window.getSelection = getSelectionBackup;
  });

  it('renders a plain translation correctly', () => {
    const { getByText } = createTranslation('', PLAIN_TRANSLATION);

    getByText(/^Un cheval/);
  });

  it('renders a Fluent translation correctly', () => {
    const { getByText } = createTranslation('fluent', FLUENT_TRANSLATION);

    getByText(/^Un cheval/);
  });

  it('renders an MF2 translation correctly', () => {
    const { getByText } = createTranslation('gettext', MF2_TRANSLATION);

    getByText(/^Un cheval/);
  });

  it('sets editor value for a plain translation', () => {
    const spy = vi.fn();
    const { getByRole } = createTranslation('', PLAIN_TRANSLATION, spy);

    fireEvent.click(getByRole('listitem'));

    expect(spy.mock.calls).toEqual([
      ['Un cheval, un cheval ! Mon royaume pour un cheval !', [], true],
    ]);
  });

  it('sets editor value for a Fluent translation', () => {
    const spy = vi.fn();
    const { container } = createTranslation('fluent', FLUENT_TRANSLATION, spy);

    fireEvent.click(container.querySelector('li'));

    expect(spy.mock.calls).toEqual([
      ['Un cheval, un cheval ! Mon royaume pour un cheval !', [], true],
    ]);
  });
});
