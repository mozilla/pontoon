import { FilterData, fetchFilterData } from '~/api/filter';
import type { AppDispatch } from '~/store';

export const UPDATE = 'search/UPDATE';
export const SET_FOCUS = 'search/SET_FOCUS';

export type Action = UpdateAction | SetFocusAction;

type UpdateAction = {
  type: typeof UPDATE;
  response: FilterData;
};

type SetFocusAction = {
  type: typeof SET_FOCUS;
  searchInputFocused: boolean;
};

export const getAuthorsAndTimeRangeData =
  (locale: string, project: string, resource: string) =>
  async (dispatch: AppDispatch) => {
    const response = await fetchFilterData(locale, project, resource);
    dispatch({ type: UPDATE, response });
  };

export function setFocus(searchInputFocused: boolean): SetFocusAction {
  return {
    type: SET_FOCUS,
    searchInputFocused,
  };
}
