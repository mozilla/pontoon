/* @flow */

import api from 'core/api';

export const RECEIVE: 'otherlocales/RECEIVE' = 'otherlocales/RECEIVE';
export const REQUEST: 'otherlocales/REQUEST' = 'otherlocales/REQUEST';


export type ReceiveAction = {|
    +type: typeof RECEIVE,
    +entity: number,
    +translations: Array<api.types.OtherLocaleTranslation>,
|};
export function receive(
    entity: number,
    translations: Array<api.types.OtherLocaleTranslation>
): ReceiveAction {
    return {
        type: RECEIVE,
        entity,
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
    return async dispatch => {
        dispatch(request(entity));

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
