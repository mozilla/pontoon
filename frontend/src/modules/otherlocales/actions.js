/* @flow */

import api from 'core/api';

import type { OtherLocaleTranslations } from 'core/api';


export const RECEIVE: 'otherlocales/RECEIVE' = 'otherlocales/RECEIVE';
export const REQUEST: 'otherlocales/REQUEST' = 'otherlocales/REQUEST';


export type ReceiveAction = {|
    +type: typeof RECEIVE,
<<<<<<< HEAD
    +translations: ?OtherLocaleTranslations,
|};
export function receive(
    translations: ?OtherLocaleTranslations
=======
    +translations: {
        preferred: Array<OtherLocaleTranslation>,
        other: Array<OtherLocaleTranslation>,
    },
|};
export function receive(
    translations: {
        preferred: Array<OtherLocaleTranslation>,
        other: Array<OtherLocaleTranslation>,
    }
>>>>>>> Initial progress to refactor frontend
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
