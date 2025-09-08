import type { Author } from '~/api/filter';

import { Action, UPDATE } from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const SEARCH = 'search';

export type SearchFilters = {
  readonly authors: Author[];
  readonly countsPerMinute: number[][];
};

const initial: SearchFilters = {
  authors: [],
  countsPerMinute: [],
};

export function reducer(
  state: SearchFilters = initial,
  action: Action,
): SearchFilters {
  switch (action.type) {
    case UPDATE:
      return {
        ...state,
        authors: action.response.authors,
        countsPerMinute: action.response.counts_per_minute,
      };
    default:
      return state;
  }
}
