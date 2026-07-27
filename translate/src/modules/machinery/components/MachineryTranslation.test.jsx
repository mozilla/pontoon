import React from 'react';

import { EntityView } from '~/context/EntityView';
import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';

import {
  ComposedTranslationComponent,
  MachineryTranslationComponent,
} from './MachineryTranslation';

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
      quality: 100,
      value: ['Cliquez'],
      properties: { title: ['Infobulle'] },
    };
    const store = createReduxStore();
    const entity = {
      format: 'fluent',
      key: ['button'],
      value: ['Click Me'],
      properties: { title: ['Tooltip'] },
    };
    const Wrapped = (props) => (
      <EntityView.Provider value={{ entity }}>
        <ComposedTranslationComponent {...props} />
      </EntityView.Provider>
    );
    const { container } = mountComponentWithStore(Wrapped, store, {
      index: 0,
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
    expect(original.textContent).toContain('Click Me');
    expect(original.textContent).toContain('Tooltip');
    expect(suggestion.textContent).toContain('Cliquez');
    expect(suggestion.textContent).toContain('Infobulle');
  });

  it('renders a single-pattern original against a multi-pattern suggestion', () => {
    // en-US declares one plural variant; the target locale needs two.
    const translation = {
      sources: ['translation-memory'],
      value: {
        decl: { count: { $: 'count', fn: 'number' } },
        sel: ['count'],
        alt: [
          { keys: ['one'], pat: ['Un popup'] },
          { keys: [{ '*': 'other' }], pat: ['Des popups'] },
        ],
      },
    };
    const store = createReduxStore();
    const entity = {
      format: 'fluent',
      key: ['popup'],
      value: ['Many popups'],
    };
    const Wrapped = (props) => (
      <EntityView.Provider value={{ entity }}>
        <ComposedTranslationComponent {...props} />
      </EntityView.Provider>
    );
    const { container } = mountComponentWithStore(Wrapped, store, {
      index: 0,
      translation,
    });
    createDefaultUser(store);

    // The original has nothing to lay out as fields, so it stays plain while
    // the suggestion still gets the rich per-variant rendering.
    expect(
      container.querySelector('.fluent-rich-string.original'),
    ).not.toBeInTheDocument();
    expect(container.querySelector('p.original').textContent).toContain(
      'Many popups',
    );

    const suggestion = container.querySelector(
      '.fluent-rich-string.suggestion',
    );
    expect(suggestion.querySelectorAll('tr')).toHaveLength(2);
    expect(suggestion.textContent).toContain('Un popup');
    expect(suggestion.textContent).toContain('Des popups');
  });
});
