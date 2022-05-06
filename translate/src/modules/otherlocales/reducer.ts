import type { OtherLocaleTranslation } from '~/api/other-locales';

import { Action, RECEIVE, REQUEST } from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const OTHERLOCALES = 'otherlocales';

export type LocalesState = {
  readonly fetching: boolean;
  readonly entity: number | null | undefined;
  readonly translations: OtherLocaleTranslation[];
};

const initialState: LocalesState = {
  fetching: false,
  entity: null,
  translations: [],
};

export function reducer(
  state: LocalesState = initialState,
  action: Action,
): LocalesState {
  switch (action.type) {
    case REQUEST:
      return {
        ...state,
        fetching: true,
        entity: action.entity,
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
