/* @flow */

import isEmpty from 'lodash.isempty';

import api from 'core/api';

import type { TranslationComment } from 'core/api';


export const RECEIVE: 'comments/RECEIVE' = 'comments/RECEIVE';
export const REQUEST: 'comments/REQUEST' = 'comments/REQUEST';


export type ReceiveAction = {|
    +type: typeof RECEIVE,
    +comments: Array<TranslationComment>,
|};
export function receive(
    comments: Array<TranslationComment>,
): ReceiveAction {
    return {
        type: RECEIVE,
        comments,
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

        let content = await api.entity.getTeamComments(entity, locale);

        // The default return value of aborted requests is {},
        // which is incompatible with reducer
        if (isEmpty(content)) {
            content = [];
        }

        dispatch(receive(content));
    }
}


export default {
    get,
    receive,
    request,
};
