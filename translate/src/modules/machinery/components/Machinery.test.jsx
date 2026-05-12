import React from 'react';

import { MachineryTranslations } from '~/context/MachineryTranslations';
import { SearchData } from '~/context/SearchData';
import { MockLocalizationProvider } from '~/test/utils';

import { Machinery } from './Machinery';
import { expect, vi } from 'vitest';
import { render } from '@testing-library/react';

vi.mock('~/hooks', () => ({
  useAppDispatch: () => () => {},
  useAppSelector: () => {},
}));
const inputPlaceholder = 'test-search';
const copyListItemTitle = 'test-copy';

const mountMachinery = (translations, search) =>
  render(
    <MockLocalizationProvider
      resources={[
        `machinery-Machinery--search-placeholder =
            .placeholder = ${inputPlaceholder}`,
        `machinery-Translation--copy = 
            .title = ${copyListItemTitle} `,
      ]}
    >
      <MachineryTranslations.Provider
        value={{ fetching: false, source: 'source', translations }}
      >
        <SearchData.Provider
          value={{
            input: '',
            query: '',
            page: 1,
            fetching: false,
            results: [],
            hasMore: false,
            setInput: () => {},
            getResults: () => {},
            ...search,
          }}
        >
          <Machinery entity={{ pk: 42 }} />
        </SearchData.Provider>
      </MachineryTranslations.Provider>
    </MockLocalizationProvider>,
  );

describe('<Machinery>', () => {
  it('shows a search form', () => {
    const { getByPlaceholderText, getByRole } = mountMachinery([], {});
    getByPlaceholderText(inputPlaceholder);
    getByRole('searchbox');
  });

  it('shows machinery translations when concordance search is not active', () => {
    const { getAllByRole, getAllByTitle } = mountMachinery(
      [
        { original: '1', sources: [] },
        { original: '2', sources: [] },
        { original: '3', sources: [] },
      ],
      {
        query: '',
        results: [
          {
            original: 'concordance-only',
            translation: 'x',
            sources: ['concordance-search'],
          },
        ],
      },
    );

    expect(getAllByRole('listitem')).toHaveLength(3);
    expect(getAllByTitle(copyListItemTitle)).toHaveLength(3);
  });

  it('shows concordance search results only when a query is active, not machinery translations', () => {
    const { getAllByRole, queryByText } = mountMachinery(
      [
        { original: 'machinery-a', sources: ['google-translate'] },
        { original: 'machinery-b', sources: ['translation-memory'] },
        { original: 'machinery-c', sources: ['translation-memory'] },
      ],
      {
        input: 'find me',
        query: 'find me',
        results: [
          {
            original: 'one',
            translation: 'uno',
            sources: ['concordance-search'],
          },
          {
            original: 'two',
            translation: 'dos',
            sources: ['concordance-search'],
          },
        ],
      },
    );

    expect(getAllByRole('listitem')).toHaveLength(2);
    expect(queryByText('machinery-a')).not.toBeInTheDocument();
    expect(queryByText('one')).toBeInTheDocument();
    expect(queryByText('two')).toBeInTheDocument();
  });

  it('shows no list rows when concordance search is active but has no results', () => {
    const { queryAllByRole } = mountMachinery(
      [
        { original: 'machinery-a', sources: ['google-translate'] },
        { original: 'machinery-b', sources: ['translation-memory'] },
      ],
      {
        input: 'nothing',
        query: 'nothing',
        results: [],
      },
    );

    expect(queryAllByRole('listitem')).toHaveLength(0);
  });

  it('renders a reset button if a search query is present', () => {
    const { getByRole } = mountMachinery([], { input: 'test', query: 'test' });
    getByRole('button');
  });

  it('shows skeleton loader when machinery is fetching and no translations exist', () => {
    const { getByTestId } = render(
      <MockLocalizationProvider resources={[]}>
        <MachineryTranslations.Provider
          value={{ fetching: true, source: '', translations: [] }}
        >
          <SearchData.Provider
            value={{
              input: '',
              query: '',
              page: 1,
              fetching: false,
              results: [],
              hasMore: false,
              setInput: () => {},
              getResults: () => {},
            }}
          >
            <Machinery entity={{ pk: 42 }} />
          </SearchData.Provider>
        </MachineryTranslations.Provider>
      </MockLocalizationProvider>,
    );
    getByTestId('machinery-skeleton-loader');
  });

  it('shows skeleton loader when machinery is fetching even if translations already exist', () => {
    const { getByTestId } = render(
      <MockLocalizationProvider resources={[]}>
        <MachineryTranslations.Provider
          value={{
            fetching: true,
            source: 'source',
            translations: [{ original: '1', translation: 'one', sources: [] }],
          }}
        >
          <SearchData.Provider
            value={{
              input: '',
              query: '',
              page: 1,
              fetching: false,
              results: [],
              hasMore: false,
              setInput: () => {},
              getResults: () => {},
            }}
          >
            <Machinery entity={{ pk: 42 }} />
          </SearchData.Provider>
        </MachineryTranslations.Provider>
      </MockLocalizationProvider>,
    );
    getByTestId('machinery-skeleton-loader');
  });
});
