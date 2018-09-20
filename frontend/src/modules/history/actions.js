/* @flow */

import api from 'core/api';

export const RECEIVE: 'history/RECEIVE' = 'history/RECEIVE';
export const REQUEST: 'history/REQUEST' = 'history/REQUEST';


export type ReceiveAction = {|
    +type: typeof RECEIVE,
    +entity: number,
    +translations: Array<Object>,
|};
export function receive(entity: number, translations: Array<Object>): ReceiveAction {
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

        const content = await api.entity.getHistory(entity, locale);

        dispatch(receive(entity, content));
    }
}


export default {
    get,
    receive,
    request,
};
