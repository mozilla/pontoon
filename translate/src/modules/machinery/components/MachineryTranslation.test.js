import React from 'react';

import { EntityView } from '~/context/EntityView';
import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';

import { MachineryTranslationComponent } from './MachineryTranslation';

const ORIGINAL = 'A horse, a horse! My kingdom for a horse!';
const DEFAULT_TRANSLATION = {
  sources: [{ type: 'translation-memory' }],
  original: ORIGINAL,
  translation: 'Un cheval, un cheval ! Mon royaume pour un cheval !',
};

function createMachineryTranslation(translation) {
  const store = createReduxStore();
  const wrapper = mountComponentWithStore(
    MachineryTranslationComponent,
    store,
    { translation },
  );
  createDefaultUser(store);
  return wrapper;
}

describe('<MachineryTranslationComponent>', () => {
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

  it('renders a translation correctly', () => {
    const { container } = createMachineryTranslation(DEFAULT_TRANSLATION);

    expect(container.querySelector('.original').textContent).toContain(
      'A horse, a horse!',
    );

    expect(container.querySelector('.suggestion').textContent).toContain(
      'Un cheval, un cheval !',
    );

    // No quality.
    expect(container.querySelector('.quality')).not.toBeInTheDocument();
  });

  it('shows quality when possible', () => {
    const translation = {
      ...DEFAULT_TRANSLATION,
      quality: 100,
    };
    const { container } = createMachineryTranslation(translation);

    expect(container.querySelector('.quality')).toBeInTheDocument();
    expect(container.querySelector('.quality')).toHaveTextContent('100%');
  });

  it('renders a composed multi-field translation as a rich table', () => {
    const translation = {
      sources: ['translation-memory'],
      composed: true,
      quality: 100,
      original: 'button = Click Me\n    .title = Tooltip\n',
      translation: 'button = Cliquez\n    .title = Infobulle\n',
    };
    const store = createReduxStore();
    const Wrapped = (props) =>
      React.createElement(
        EntityView.Provider,
        { value: { entity: { format: 'fluent' } } },
        React.createElement(MachineryTranslationComponent, props),
      );
    const { container } = mountComponentWithStore(Wrapped, store, {
      translation,
    });
    createDefaultUser(store);

    // Each leaf (value + attribute) is shown as a labeled row, on both the
    // original and the suggestion side.
    const original = container.querySelector('.fluent-rich-string.original');
    const suggestion = container.querySelector(
      '.fluent-rich-string.suggestion',
    );
    expect(original).toBeInTheDocument();
    expect(suggestion).toBeInTheDocument();
    expect(original.querySelectorAll('tr')).toHaveLength(2);
    expect(suggestion.textContent).toContain('Cliquez');
    expect(suggestion.textContent).toContain('Infobulle');
  });
});
