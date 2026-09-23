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
