import { FilterData, fetchFilterData } from '~/api/filter';
import type { AppDispatch } from '~/store';

export const UPDATE = 'search/UPDATE';

export type Action = UpdateAction;

type UpdateAction = {
  type: typeof UPDATE;
  response: FilterData;
};

export const getAuthorsAndTimeRangeData =
  (locale: string, project: string, resource: string) =>
  async (dispatch: AppDispatch) => {
    const response = await fetchFilterData(locale, project, resource);
    dispatch({ type: UPDATE, response });
  };
