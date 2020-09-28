/* @flow */

import isEmpty from 'lodash.isempty';

import api from 'core/api';

import type { OtherLocaleTranslations } from 'core/api';

export const RECEIVE: 'otherlocales/RECEIVE' = 'otherlocales/RECEIVE';
export const REQUEST: 'otherlocales/REQUEST' = 'otherlocales/REQUEST';

export type ReceiveAction = {|
    +type: typeof RECEIVE,
    +translations: ?OtherLocaleTranslations,
|};
export function receive(translations: ?OtherLocaleTranslations): ReceiveAction {
    return {
        type: RECEIVE,
        translations,
    };
}

export type RequestAction = {|
    +type: typeof REQUEST,
    +entity: number,
|};
export function request(entity: number): RequestAction {
    return {
        type: REQUEST,
        entity,
    };
}

export function get(entity: number, locale: string): Function {
    return async (dispatch) => {
        dispatch(request(entity));

        // Abort all previously running requests.
        await api.entity.abort();

        let content = await api.entity.getOtherLocales(entity, locale);

        // The default return value of aborted requests is {},
        // which is incompatible with reducer
        if (isEmpty(content)) {
            content = null;
        }

        dispatch(receive(content));
    };
}

export default {
    get,
    receive,
    request,
};
