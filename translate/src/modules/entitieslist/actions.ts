import type { AppDispatch } from '~/store';

export const TOGGLE = 'entitieslist/TOGGLE';

export type Action = ToggleAction;

type ToggleAction = {
  readonly type: typeof TOGGLE;
  readonly show: boolean;
};

/**
 * Toggle Entities List (used in mobile view).
 */
export const toggleEntitiesList = () => async (dispatch: AppDispatch) => {
  dispatch({
    type: TOGGLE,
  });
};
