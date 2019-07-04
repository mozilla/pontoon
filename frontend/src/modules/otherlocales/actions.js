/* @flow */

import api from 'core/api';

import type { OtherLocaleTranslation } from 'core/api';


export const RECEIVE: 'otherlocales/RECEIVE' = 'otherlocales/RECEIVE';
export const REQUEST: 'otherlocales/REQUEST' = 'otherlocales/REQUEST';


export type ReceiveAction = {|
    +type: typeof RECEIVE,
    +entity: number,
    +translations: Array<OtherLocaleTranslation>,
|};
export function receive(
    entity: number,
    translations: Array<OtherLocaleTranslation>
): ReceiveAction {
    return {
        type: RECEIVE,
        entity,
        translations,
    };
}


export type RequestAction = {|
    +type: typeof REQUEST,
|};
export function request(): RequestAction {
    return {
        type: REQUEST,
    };
}


export function get(entity: number, locale: string): Function {
    return async dispatch => {
        dispatch(request());

        // Abort all previously running requests.
        await api.entity.abort();

        const content = await api.entity.getOtherLocales(entity, locale);

        dispatch(receive(entity, content));
    }
}


export default {
    get,
    receive,
    request,
};
