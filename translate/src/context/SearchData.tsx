import React, { createContext, useContext, useEffect, useState } from 'react';

import { fetchConcordanceResults, MachineryTranslation } from '~/api/machinery';
import { EntityView } from './EntityView';

import { Locale } from './Locale';

export type SearchData = {
  /** The value in the search field */
  input: string;

  /** Once submitted, the query matching the current results */
  query: string;

  /** Last fetched page (1-indexed) */
  page: number;

  /** If `true`, results are being fetched */
  fetching: boolean;

  results: MachineryTranslation[];

  /** If true, calling `getResults()` will append entries to `results` */
  hasMore: boolean;

  /** Set the `input` value and stop fetching additional results */
  setInput(input: string): void;

  /**
   * If `input` and `query` differ, set `query = input` and fetch new results.
   * If they are the same and `hasMore` is `true`, fetch additional results.
   */
  getResults(): void;
};

const initSearch: SearchData = {
  input: '',
  query: '',
  page: 1,
  fetching: false,
  results: [],
  hasMore: false,
  setInput: () => {},
  getResults: () => {},
};

export const SearchData = createContext<SearchData>(initSearch);

export function SearchProvider({ children }: { children: React.ReactElement }) {
  const locale = useContext(Locale);
  const { entity } = useContext(EntityView);

  const [search, setSearch] = useState<SearchData>(() => ({
    ...initSearch,
    setInput(input) {
      setSearch((prev) =>
        prev.input === input ? prev : { ...prev, input, hasMore: false },
      );
    },
    getResults() {
      setSearch((prev) => {
        if (prev.input === prev.query) {
          return prev.hasMore
            ? { ...prev, page: prev.page + 1, fetching: true }
            : prev;
        } else {
          const query = prev.input;
          return { ...prev, query, page: 1, results: [], fetching: !!query };
        }
      });
    },
  }));

  const { setInput, query, page, fetching } = search;

  useEffect(() => setInput(''), [entity]);

  useEffect(() => {
    if (fetching) {
      fetchConcordanceResults(query, locale, page).then(
        ({ results, hasMore }) => {
          setSearch((prev) =>
            prev.query !== query
              ? prev // Let's not clobber the results if the query has changed
              : {
                  ...prev,
                  fetching: false,
                  results: prev.results.concat(results),
                  hasMore,
                },
          );
        },
      );
    }
  }, [query, page]);

  return <SearchData.Provider value={search}>{children}</SearchData.Provider>;
}
