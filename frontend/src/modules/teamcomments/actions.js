/* @flow */

import api from 'core/api';

import type { TeamComment } from 'core/api';


export const RECEIVE: 'comments/RECEIVE' = 'comments/RECEIVE';
export const REQUEST: 'comments/REQUEST' = 'comments/REQUEST';


export type ReceiveAction = {|
    +type: typeof RECEIVE,
    +comments: Array<TeamComment>,
|};
export function receive(
    comments: Array<TeamComment>,
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
        // Abort all previously running requests.
        await api.entity.abort();

        let content = await api.entity.getTeamComments(entity, locale);

        dispatch(receive(content));
    }
}


export default {
    get,
    receive,
    request,
};
