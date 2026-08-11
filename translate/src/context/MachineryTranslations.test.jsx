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
  fetchGPTTransform: vi.fn(() => Promise.resolve([])),
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
  return <span data-testid='count'>{translations.length}</span>;
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

    await waitFor(() => expect(api.fetchGPTTransform).toHaveBeenCalled());

    const [source, references, characteristic, code, pk, trigger] =
      api.fetchGPTTransform.mock.calls[0];
    expect(source).toBe('Hello');
    expect(references).toEqual([{ source: 'google-translate', text: 'Hola' }]);
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

      await waitFor(() => expect(api.fetchGPTTransform).toHaveBeenCalled());
    },
  );

  it('skips strings that already have an approved translation', async () => {
    setRootFlags({ enabled: true });
    mount(
      entityOf({ pk: 1, status: 'approved', string: 'Hola', value: ['Hola'] }),
    );

    await waitFor(() => expect(api.fetchGoogleTranslation).toHaveBeenCalled());
    expect(api.fetchGPTTransform).not.toHaveBeenCalled();
  });

  it('skips locales it is not enabled for', async () => {
    setRootFlags({ enabled: false });
    mount(entityOf(undefined));

    await waitFor(() => expect(api.fetchGoogleTranslation).toHaveBeenCalled());
    expect(api.fetchGPTTransform).not.toHaveBeenCalled();
  });

  it('skips when Google Translate returns nothing to refine', async () => {
    setRootFlags({ enabled: true });
    api.fetchGoogleTranslation.mockResolvedValue([]);
    mount(entityOf(undefined));

    await waitFor(() => expect(api.fetchGoogleTranslation).toHaveBeenCalled());
    expect(api.fetchGPTTransform).not.toHaveBeenCalled();
  });
});
