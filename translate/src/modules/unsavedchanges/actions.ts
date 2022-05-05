import type { AppStore } from '~/hooks';
import type { AppDispatch } from '~/store';

import { NAME } from './reducer';

export const HIDE_UNSAVED_CHANGES = 'unsavedchanges/HIDE';
export const IGNORE_UNSAVED_CHANGES = 'unsavedchanges/IGNORE';
export const SHOW_UNSAVED_CHANGES = 'unsavedchanges/SHOW';
export const UPDATE_UNSAVED_CHANGES = 'unsavedchanges/UPDATE';

export type Action = HideAction | IgnoreAction | ShowAction | UpdateAction;

type HideAction = { type: typeof HIDE_UNSAVED_CHANGES };
type IgnoreAction = { type: typeof IGNORE_UNSAVED_CHANGES };
type ShowAction = {
  type: typeof SHOW_UNSAVED_CHANGES;
  callback: () => void;
};
type UpdateAction = {
  type: typeof UPDATE_UNSAVED_CHANGES;
  exist: boolean;
};

/**
 * Check if the editor has unsaved changes by comparing its content
 * with the active translation. Show unsaved changes if they exist and
 * aren't explicitly ignored, or else execute callback function.
 */
export const checkUnsavedChanges =
  (store: AppStore, callback: () => void) => (dispatch: AppDispatch) => {
    const state = store.getState();
    const { exist, ignored } = state[NAME];
    if (exist && !ignored) {
      dispatch({ type: SHOW_UNSAVED_CHANGES, callback });
    } else {
      callback();
    }
  };

/**
 * Hide unsaved changes notice.
 */
export const hideUnsavedChanges = (): HideAction => ({
  type: HIDE_UNSAVED_CHANGES,
});

/**
 * Ignore unsaved changes notice ("Proceed").
 */
export const ignoreUnsavedChanges = (): IgnoreAction => ({
  type: IGNORE_UNSAVED_CHANGES,
});

/**
 * Update unsaved changes status.
 */
export const updateUnsavedChanges = (exist: boolean): UpdateAction => ({
  type: UPDATE_UNSAVED_CHANGES,
  exist,
});
