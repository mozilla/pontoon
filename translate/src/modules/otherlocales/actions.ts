import { fetchOtherLocales, OtherLocaleTranslation } from '../../../src/api/other-locales';
import type { AppDispatch } from '../../store';

export const RECEIVE: 'otherlocales/RECEIVE' = 'otherlocales/RECEIVE';
export const REQUEST: 'otherlocales/REQUEST' = 'otherlocales/REQUEST';

export type Action = ReceiveAction | RequestAction;

export type ReceiveAction = {
  readonly type: typeof RECEIVE;
  readonly translations: OtherLocaleTranslation[];
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
    const translations = await fetchOtherLocales(entity, locale);
    dispatch({ type: RECEIVE, translations });
  };
}
