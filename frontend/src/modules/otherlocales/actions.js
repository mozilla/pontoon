/* @flow */

import api from 'core/api';

import type { OtherLocaleTranslation } from 'core/api';


export const RECEIVE: 'otherlocales/RECEIVE' = 'otherlocales/RECEIVE';
export const REQUEST: 'otherlocales/REQUEST' = 'otherlocales/REQUEST';


export type ReceiveAction = {|
    +type: typeof RECEIVE,
    +translations: Array<OtherLocaleTranslation>,
|};
export function receive(
    translations: Array<OtherLocaleTranslation>
): ReceiveAction {
    return {
        type: RECEIVE,
        translations,
    };
}


export type RequestAction = {|
    +type: typeof REQUEST,
    +entity: number,
|};
export function request(
    entity: number,
): RequestAction {
    return {
        type: REQUEST,
        entity,
    };
}


export function get(entity: number, locale: string): Function {
    return async dispatch => {
        dispatch(request(entity));

        // Abort all previously running requests.
        await api.entity.abort();

        const content = await api.entity.getOtherLocales(entity, locale);

        dispatch(receive(content));
    }
}


export default {
    get,
    receive,
    request,
};
