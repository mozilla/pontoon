import { Action, TOGGLE } from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const ENTITIESLIST = 'entitieslist';

export type EntitiesListState = {
  readonly show: boolean;
};

const initial: EntitiesListState = {
  show: false,
};

export function reducer(
  state: EntitiesListState = initial,
  action: Action,
): EntitiesListState {
  switch (action.type) {
    case TOGGLE:
      return {
        ...state,
        show: !state.show,
      };
    default:
      return state;
  }
}
