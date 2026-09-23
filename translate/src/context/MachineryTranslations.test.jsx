import React, { useContext } from 'react';
import { render, waitFor } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach } from 'vitest';

import * as api from '~/api/machinery';

import { EntityView } from './EntityView';
import { Locale } from './Locale';
import {
  MachineryProvider,
  MachineryTranslations,
} from './MachineryTranslations';
import { SearchData } from './SearchData';

vi.mock('~/api/machinery', () => ({
  abortMachineryRequests: vi.fn(),
  fetchCaighdeanTranslation: vi.fn(() => Promise.resolve([])),
  fetchComposedMachinery: vi.fn(() => Promise.resolve([])),
  fetchGoogleTranslation: vi.fn(() => Promise.resolve([])),
  fetchOpenAIComposedTranslation: vi.fn(() => Promise.resolve(null)),
  fetchOpenAITranslation: vi.fn(() => Promise.resolve([])),
  fetchMicrosoftTranslation: vi.fn(() => Promise.resolve([])),
  fetchTranslationMemory: vi.fn(() => Promise.resolve([])),
}));

vi.mock('~/hooks', () => ({
  useAppSelector: () => ({ isAuthenticated: true }),
}));

const GT_RESULT = [
  { sources: ['google-translate'], original: 'Hello', translation: 'Hola' },
];

const locale = {
  code: 'es',
  googleTranslateCode: 'es',
  msTranslatorCode: '',
  cldrPlurals: [1, 5],
};

const entityOf = (translation) => ({
  pk: 42,
  key: ['greeting'],
  format: 'po',
  original: 'Hello',
  value: ['Hello'],
  comment: '',
  date_created: '',
  path: '',
  project: {},
  translation,
});

function Consumer() {
  const { translations } = useContext(MachineryTranslations);
  return (
    <span data-testid='order'>
      {translations.map((t) => t.sources.join('+')).join(',')}
    </span>
  );
}

const mount = (entity) =>
  render(
    <Locale.Provider value={locale}>
      <EntityView.Provider value={{ entity }}>
        <SearchData.Provider value={{ query: '' }}>
          <MachineryProvider>
            <Consumer />
          </MachineryProvider>
        </SearchData.Provider>
      </EntityView.Provider>
    </Locale.Provider>,
  );

function setRootFlags({ enabled }) {
  let root = document.getElementById('root');
  if (!root) {
    root = document.createElement('div');
    root.id = 'root';
    document.body.appendChild(root);
  }
  root.dataset.isGoogleTranslateSupported = 'true';
  root.dataset.isMicrosoftTranslatorSupported = 'false';
  root.dataset.isLlmAutoSuggestionLocale = String(enabled);
}

describe('<MachineryProvider> automatic LLM suggestions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.fetchGoogleTranslation.mockResolvedValue(GT_RESULT);
  });

  it('requests a suggestion for a string without a translation', async () => {
    setRootFlags({ enabled: true });
    mount(entityOf(undefined));

    await waitFor(() => expect(api.fetchOpenAITranslation).toHaveBeenCalled());

    const [source, references, characteristic, code, pk, trigger] =
      api.fetchOpenAITranslation.mock.calls[0];
    expect(source).toBe('Hello');
    expect(references).toEqual({ 'google-translate': ['Hola'] });
    expect(characteristic).toBe('rephrased');
    expect(code).toBe('es');
    expect(pk).toBe(42);
    expect(trigger).toBe('auto');
  });

  it.each(['fuzzy', 'pretranslated', 'rejected', 'unreviewed'])(
    'requests a suggestion when the translation is %s',
    async (status) => {
      setRootFlags({ enabled: true });
      mount(entityOf({ pk: 1, status, string: 'Hola', value: ['Hola'] }));

      await waitFor(() =>
        expect(api.fetchOpenAITranslation).toHaveBeenCalled(),
      );
    },
  );

  it('skips strings that already have an approved translation', async () => {
    setRootFlags({ enabled: true });
    mount(
      entityOf({ pk: 1, status: 'approved', string: 'Hola', value: ['Hola'] }),
    );

    await waitFor(() => expect(api.fetchGoogleTranslation).toHaveBeenCalled());
    expect(api.fetchOpenAITranslation).not.toHaveBeenCalled();
  });

  it('skips locales it is not enabled for', async () => {
    setRootFlags({ enabled: false });
    mount(entityOf(undefined));

    await waitFor(() => expect(api.fetchGoogleTranslation).toHaveBeenCalled());
    expect(api.fetchOpenAITranslation).not.toHaveBeenCalled();
  });

  it('skips when the user moved on before Google Translate resolved', async () => {
    setRootFlags({ enabled: true });
    let resolveGoogle;
    api.fetchGoogleTranslation.mockReturnValue(
      new Promise((resolve) => {
        resolveGoogle = resolve;
      }),
    );

    const { unmount } = mount(entityOf(undefined));
    unmount();
    resolveGoogle(GT_RESULT);
    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(api.fetchOpenAITranslation).not.toHaveBeenCalled();
  });

  it('skips when Google Translate returns nothing to refine', async () => {
    setRootFlags({ enabled: true });
    api.fetchGoogleTranslation.mockResolvedValue([]);
    mount(entityOf(undefined));

    await waitFor(() => expect(api.fetchGoogleTranslation).toHaveBeenCalled());
    expect(api.fetchOpenAITranslation).not.toHaveBeenCalled();
  });

  it('lists the suggestion last, below the result it refines', async () => {
    setRootFlags({ enabled: true });
    api.fetchOpenAITranslation.mockResolvedValue([
      {
        sources: ['openai-chatgpt'],
        original: 'Hello',
        translation: 'Saludos',
      },
    ]);
    // Resolves last, to show that a scored match still sorts to the top while
    // the scoreless ones keep the order they arrived in.
    let resolveMemory;
    api.fetchTranslationMemory.mockReturnValue(
      new Promise((resolve) => {
        resolveMemory = resolve;
      }),
    );

    const { getByTestId } = mount(entityOf(undefined));

    await waitFor(() =>
      expect(getByTestId('order').textContent).toContain('openai-chatgpt'),
    );
    resolveMemory([
      {
        sources: ['translation-memory'],
        original: 'Hello',
        translation: 'Buenos días',
        quality: 90,
      },
    ]);

    await waitFor(() =>
      expect(getByTestId('order').textContent).toBe(
        'translation-memory,google-translate,openai-chatgpt',
      ),
    );
  });
});

describe('<MachineryProvider> automatic composed LLM suggestions', () => {
  // Two leaves, so `hasMultipleFields()` asks for a composed suggestion.
  const multiFieldEntity = (translation) => ({
    ...entityOf(translation),
    format: 'fluent',
    properties: { title: ['Tooltip'] },
  });

  const COMPOSED_GT = [
    {
      sources: ['google-translate'],
      value: ['Hola'],
      properties: { title: ['Sugerencia'] },
    },
  ];

  function ComposedConsumer() {
    const { composed } = useContext(MachineryTranslations);
    return (
      <span data-testid='composed'>
        {composed.map((t) => t.sources.join('+')).join(',')}
      </span>
    );
  }

  const mountComposed = (entity) =>
    render(
      <Locale.Provider value={locale}>
        <EntityView.Provider value={{ entity }}>
          <SearchData.Provider value={{ query: '' }}>
            <MachineryProvider>
              <ComposedConsumer />
            </MachineryProvider>
          </SearchData.Provider>
        </EntityView.Provider>
      </Locale.Provider>,
    );

  beforeEach(() => {
    vi.clearAllMocks();
    api.fetchGoogleTranslation.mockResolvedValue(GT_RESULT);
    api.fetchComposedMachinery.mockImplementation((_pk, _locale, service) =>
      Promise.resolve(service === 'google-translate' ? COMPOSED_GT : []),
    );
  });

  it('refines the Google-Translate-backed composition', async () => {
    setRootFlags({ enabled: true });
    api.fetchOpenAIComposedTranslation.mockResolvedValue({
      value: ['Saludos'],
      properties: { title: ['Refinada'] },
    });

    const { getByTestId } = mountComposed(multiFieldEntity(undefined));

    await waitFor(() =>
      expect(api.fetchOpenAIComposedTranslation).toHaveBeenCalled(),
    );

    const [pk, value, properties, characteristic, code, trigger] =
      api.fetchOpenAIComposedTranslation.mock.calls[0];
    expect(pk).toBe(42);
    expect(value).toEqual(['Hola']);
    expect(properties).toEqual({ title: ['Sugerencia'] });
    expect(characteristic).toBe('rephrased');
    expect(code).toBe('es');
    expect(trigger).toBe('auto');

    await waitFor(() =>
      expect(getByTestId('composed').textContent).toBe(
        'google-translate,openai-chatgpt',
      ),
    );
  });

  it('replaces the single-string suggestion rather than adding to it', async () => {
    // One automatic call per string: refining the flattened string would only
    // ever fill the focused field.
    setRootFlags({ enabled: true });
    api.fetchOpenAIComposedTranslation.mockResolvedValue({
      value: ['Saludos'],
      properties: { title: ['Refinada'] },
    });

    mountComposed(multiFieldEntity(undefined));

    await waitFor(() =>
      expect(api.fetchOpenAIComposedTranslation).toHaveBeenCalled(),
    );
    expect(api.fetchOpenAITranslation).not.toHaveBeenCalled();
  });

  it('merges the sources when the LLM returns the composition unchanged', async () => {
    setRootFlags({ enabled: true });
    api.fetchOpenAIComposedTranslation.mockResolvedValue({
      value: ['Hola'],
      properties: { title: ['Sugerencia'] },
    });

    const { getByTestId } = mountComposed(multiFieldEntity(undefined));

    await waitFor(() =>
      expect(getByTestId('composed').textContent).toBe(
        'google-translate+openai-chatgpt',
      ),
    );
  });

  it('skips strings that already have an approved translation', async () => {
    setRootFlags({ enabled: true });
    mountComposed(
      multiFieldEntity({
        pk: 1,
        status: 'approved',
        string: 'Hola',
        value: ['Hola'],
      }),
    );

    await waitFor(() => expect(api.fetchComposedMachinery).toHaveBeenCalled());
    expect(api.fetchOpenAIComposedTranslation).not.toHaveBeenCalled();
  });

  it('skips locales it is not enabled for', async () => {
    setRootFlags({ enabled: false });
    mountComposed(multiFieldEntity(undefined));

    await waitFor(() => expect(api.fetchComposedMachinery).toHaveBeenCalled());
    expect(api.fetchOpenAIComposedTranslation).not.toHaveBeenCalled();
  });

  it('skips single-field entities, which have no composition to refine', async () => {
    setRootFlags({ enabled: true });
    mountComposed(entityOf(undefined));

    await waitFor(() => expect(api.fetchGoogleTranslation).toHaveBeenCalled());
    expect(api.fetchComposedMachinery).not.toHaveBeenCalled();
    expect(api.fetchOpenAIComposedTranslation).not.toHaveBeenCalled();
  });

  it('skips when the composed request returns nothing to refine', async () => {
    setRootFlags({ enabled: true });
    api.fetchComposedMachinery.mockResolvedValue([]);
    mountComposed(multiFieldEntity(undefined));

    await waitFor(() => expect(api.fetchComposedMachinery).toHaveBeenCalled());
    expect(api.fetchOpenAIComposedTranslation).not.toHaveBeenCalled();
  });

  it('skips when the user moved on before the composition resolved', async () => {
    setRootFlags({ enabled: true });
    let resolveComposed;
    api.fetchComposedMachinery.mockImplementation((_pk, _locale, service) =>
      service === 'google-translate'
        ? new Promise((resolve) => {
            resolveComposed = resolve;
          })
        : Promise.resolve([]),
    );

    const { unmount } = mountComposed(multiFieldEntity(undefined));
    unmount();
    resolveComposed(COMPOSED_GT);
    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(api.fetchOpenAIComposedTranslation).not.toHaveBeenCalled();
  });
});

describe('<MachineryProvider> result merging', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setRootFlags({ enabled: false });
  });

  it('keeps the suggestion object when a later result merges into it', () => {
    // LLM refinement state is keyed by this object in a WeakMap, so replacing
    // it mid-refinement would strand the answer under a key nothing renders.
    const seen = [];

    function IdentityConsumer() {
      const { translations } = useContext(MachineryTranslations);
      if (translations[0]) {
        seen.push(translations[0]);
      }
      return (
        <span data-testid='order'>
          {translations.map((t) => t.sources.join('+')).join(',')}
        </span>
      );
    }

    // Translation Memory and Google Translate return the same string, so the
    // two rows merge into one.
    api.fetchTranslationMemory.mockResolvedValue([
      {
        sources: ['translation-memory'],
        original: 'Hello',
        translation: 'Hola',
        quality: 90,
      },
    ]);
    api.fetchGoogleTranslation.mockResolvedValue(GT_RESULT);

    const { getByTestId } = render(
      <Locale.Provider value={locale}>
        <EntityView.Provider value={{ entity: entityOf(undefined) }}>
          <SearchData.Provider value={{ query: '' }}>
            <MachineryProvider>
              <IdentityConsumer />
            </MachineryProvider>
          </SearchData.Provider>
        </EntityView.Provider>
      </Locale.Provider>,
    );

    return waitFor(() => {
      expect(getByTestId('order').textContent).toBe(
        'translation-memory+google-translate',
      );
      expect(new Set(seen).size).toBe(1);
    });
  });
});
