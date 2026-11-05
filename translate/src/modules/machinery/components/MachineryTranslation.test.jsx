import React from 'react';
import { act, fireEvent, screen } from '@testing-library/react';
import { vi } from 'vitest';

import * as machineryApi from '~/api/machinery';
import { EntityView } from '~/context/EntityView';
import { LLMTranslationProvider } from '~/context/TranslationContext';
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
  describe('AI refinement', () => {
    const ENTITY = {
      pk: 42,
      format: 'fluent',
      key: ['button'],
      value: ['Click Me'],
      properties: { title: ['Tooltip'] },
    };
    const COMPOSED = {
      sources: ['translation-memory', 'google-translate'],
      value: ['Cliquez'],
      properties: { title: ['Infobulle'] },
    };

    let root;

    beforeEach(() => {
      root = document.createElement('div');
      root.id = 'root';
      root.dataset.isOpenaiChatgptSupported = 'true';
      document.body.appendChild(root);
    });

    afterEach(() => {
      root.remove();
      vi.restoreAllMocks();
    });

    function mountComposed(translation = COMPOSED, entity = ENTITY) {
      const store = createReduxStore();
      const Wrapped = (props) => (
        <EntityView.Provider value={{ entity }}>
          <LLMTranslationProvider>
            <ComposedTranslationComponent {...props} />
          </LLMTranslationProvider>
        </EntityView.Provider>
      );
      const result = mountComponentWithStore(Wrapped, store, {
        index: 0,
        translation,
      });
      createDefaultUser(store);
      return result;
    }

    it('offers the AI dropdown on a composed suggestion', () => {
      const { container } = mountComposed();
      const sources = container.querySelector('ul.sources');
      expect(sources.lastElementChild).toHaveClass('ai-refine');
    });

    it('does not offer to refine a suggestion that is already LLM output', () => {
      const { container } = mountComposed({
        ...COMPOSED,
        sources: ['openai-chatgpt'],
      });
      expect(container.querySelector('li.ai-refine')).not.toBeInTheDocument();
    });

    it('hides the dropdown when OpenAI is not supported', () => {
      root.dataset.isOpenaiChatgptSupported = 'false';
      const { container } = mountComposed();
      expect(container.querySelector('li.ai-refine')).not.toBeInTheDocument();
    });

    it('replaces every field with the refined translation', async () => {
      const fetchRefined = vi
        .spyOn(machineryApi, 'fetchOpenAIComposedTranslation')
        .mockResolvedValue({
          value: ['Veuillez cliquer'],
          properties: { title: ['Infobulle raffinée'] },
        });

      const { container } = mountComposed();

      fireEvent.click(container.querySelector('li.ai-refine .selector'));
      await act(async () => {
        fireEvent.click(screen.getByText('MAKE FORMAL'));
      });

      expect(fetchRefined).toHaveBeenCalledWith(
        42,
        COMPOSED.value,
        COMPOSED.properties,
        'formal',
        expect.anything(),
      );

      const suggestion = container.querySelector(
        '.fluent-rich-string.suggestion',
      );
      expect(suggestion.textContent).toContain('Veuillez cliquer');
      expect(suggestion.textContent).toContain('Infobulle raffinée');
      expect(suggestion.textContent).not.toContain('Cliquez');

      expect(
        container.querySelector('.fluent-rich-string.original').textContent,
      ).toContain('Click Me');
      expect(container.querySelector('.selected-option').textContent).toContain(
        'formal',
      );
    });

    it('restores the unrefined suggestion', async () => {
      vi.spyOn(
        machineryApi,
        'fetchOpenAIComposedTranslation',
      ).mockResolvedValue({
        value: ['Veuillez cliquer'],
        properties: { title: ['Raffiné'] },
      });

      const { container } = mountComposed();

      fireEvent.click(container.querySelector('li.ai-refine .selector'));
      await act(async () => {
        fireEvent.click(screen.getByText('MAKE FORMAL'));
      });

      fireEvent.click(container.querySelector('li.ai-refine .selector'));
      await act(async () => {
        fireEvent.click(screen.getByText('SHOW ORIGINAL'));
      });

      expect(
        container.querySelector('.fluent-rich-string.suggestion').textContent,
      ).toContain('Cliquez');
    });

    it('keeps the suggestion when refinement fails', async () => {
      vi.spyOn(
        machineryApi,
        'fetchOpenAIComposedTranslation',
      ).mockResolvedValue(null);

      const { container } = mountComposed();

      fireEvent.click(container.querySelector('li.ai-refine .selector'));
      await act(async () => {
        fireEvent.click(screen.getByText('REPHRASE'));
      });

      expect(
        container.querySelector('.fluent-rich-string.suggestion').textContent,
      ).toContain('Cliquez');
      expect(container.querySelector('.selected-option').textContent).toBe('');
    });
  });
});
