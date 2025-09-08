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
  readonly sourceString: string;
};
export function request(sourceString: string): RequestAction {
  return {
    type: REQUEST,
    sourceString,
  };
}

export function get(sourceString: string, locale: string) {
  return async (dispatch: AppDispatch) => {
    dispatch(request(sourceString));
    const terms = await fetchTerms(sourceString, locale);
    dispatch({ type: RECEIVE, terms });
  };
}
