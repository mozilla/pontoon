import type { Author } from '~/api/filter';

import { Action, UPDATE, SET_FOCUS } from './actions';

export type SearchAndFilters = {
  readonly authors: Author[];
  readonly countsPerMinute: number[][];
  readonly searchInputFocused: boolean;
};

const initial: SearchAndFilters = {
  authors: [],
  countsPerMinute: [],
  searchInputFocused: false,
};

export default function reducer(
  state: SearchAndFilters = initial,
  action: Action,
): SearchAndFilters {
  switch (action.type) {
    case UPDATE:
      return {
        ...state,
        authors: action.response.authors,
        countsPerMinute: action.response.counts_per_minute,
      };
    case SET_FOCUS:
      return {
        ...state,
        searchInputFocused: action.searchInputFocused,
      };
    default:
      return state;
  }
}
