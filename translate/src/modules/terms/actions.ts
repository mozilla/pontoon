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
  readonly locale: string;
};
export function request(entity: number, locale: string): RequestAction {
  return {
    type: REQUEST,
    entity,
    locale,
  };
}

export function get(entity: number, locale: string) {
  return async (dispatch: AppDispatch) => {
    dispatch(request(entity, locale));
    const terms = await fetchTerms(entity, locale);
    dispatch({ type: RECEIVE, terms });
  };
}
