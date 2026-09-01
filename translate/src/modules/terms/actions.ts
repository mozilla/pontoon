import { fetchTerms, TermType } from '~/api/terminology';
import type { AppDispatch } from '~/store';

export const RECEIVE = 'terms/RECEIVE';
export const REQUEST = 'terms/REQUEST';

export type Action = ReceiveAction | RequestAction;

export type ReceiveAction = {
  readonly type: typeof RECEIVE;
  readonly terms: Array<TermType>;
};

export type RequestAction = {
  readonly type: typeof REQUEST;
  readonly entity: number;
};
export function request(entity: number): RequestAction {
  return {
    type: REQUEST,
    entity,
  };
}

export function get(entity: number, locale: string) {
  return async (dispatch: AppDispatch) => {
    dispatch(request(entity));
    const terms = await fetchTerms(entity, locale);
    dispatch({ type: RECEIVE, terms });
  };
}
