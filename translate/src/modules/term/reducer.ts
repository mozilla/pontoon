import type { TermType } from '~/api/terminology';

import { Action, RECEIVE, REQUEST } from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const TERM = 'term';

export type TermState = {
  readonly fetching: boolean;
  readonly sourceString: string;
  readonly terms: Array<TermType>;
};

const initialState: TermState = {
  fetching: false,
  sourceString: '',
  terms: [],
};

export function reducer(
  state: TermState = initialState,
  action: Action,
): TermState {
  switch (action.type) {
    case REQUEST:
      return {
        ...state,
        fetching: true,
        sourceString: action.sourceString,
        terms: [],
      };
    case RECEIVE:
      return {
        ...state,
        fetching: false,
        terms: action.terms,
      };
    default:
      return state;
  }
}
