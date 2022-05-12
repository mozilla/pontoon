import { HistoryTranslation } from '~/api/translation';

import { Action, RECEIVE, REQUEST, UPDATE } from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const HISTORY = 'history';

export type HistoryState = {
  readonly fetching: boolean;
  readonly entity: number | null | undefined;
  readonly pluralForm: number | null | undefined;
  readonly translations: Array<HistoryTranslation>;
};

function updateTranslation(
  translations: Array<HistoryTranslation>,
  newTranslation: HistoryTranslation,
) {
  return translations.map((translation) => {
    if (translation.pk === newTranslation.pk) {
      return { ...translation, ...newTranslation };
    }
    return translation;
  });
}

const initialState: HistoryState = {
  fetching: false,
  entity: null,
  pluralForm: null,
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
        entity: action.entity,
        pluralForm: action.pluralForm,
        translations: [],
      };
    case RECEIVE:
      return {
        ...state,
        fetching: false,
        translations: action.translations,
      };
    case UPDATE:
      return {
        ...state,
        translations: updateTranslation(state.translations, action.translation),
      };
    default:
      return state;
  }
}
