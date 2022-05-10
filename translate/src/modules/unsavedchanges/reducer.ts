import {
  Action,
  HIDE_UNSAVED_CHANGES,
  IGNORE_UNSAVED_CHANGES,
  SHOW_UNSAVED_CHANGES,
  UPDATE_UNSAVED_CHANGES,
} from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME = 'unsavedchanges';

export type UnsavedChangesState = {
  readonly callback: (() => void) | null;
  readonly exist: boolean;
  readonly ignored: boolean;
  readonly shown: boolean;
};

const initialState: UnsavedChangesState = {
  callback: null,
  exist: false,
  ignored: false,
  shown: false,
};

export function reducer(
  state: UnsavedChangesState = initialState,
  action: Action,
): UnsavedChangesState {
  switch (action.type) {
    case HIDE_UNSAVED_CHANGES:
      return { ...initialState };
    case IGNORE_UNSAVED_CHANGES:
      return {
        ...state,
        ignored: true,
      };
    case SHOW_UNSAVED_CHANGES:
      return {
        ...state,
        shown: true,
        callback: action.callback,
      };
    case UPDATE_UNSAVED_CHANGES:
      return {
        ...state,
        exist: action.exist,
        ignored: false,
      };
    default:
      return state;
  }
}
