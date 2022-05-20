import { HistoryTranslation } from '~/api/translation';

import { Action, RECEIVE, REQUEST } from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const HISTORY = 'history';

type HistoryState = {
  readonly fetching: boolean;
  readonly translations: Array<HistoryTranslation>;
};

const initialState: HistoryState = {
  fetching: false,
  translations: [],
};

export function reducer(
  state: HistoryState = initialState,
  action: Action,
): HistoryState {
  switch (action.type) {
    case REQUEST:
      return {
        ...state,
        fetching: true,
        translations: [],
      };
    case RECEIVE:
      return {
        ...state,
        fetching: false,
        translations: action.translations,
      };
    default:
      return state;
  }
}
