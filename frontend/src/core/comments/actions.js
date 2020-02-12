/* @flow */

import isEmpty from 'lodash.isempty';
import NProgress from 'nprogress';

import api from 'core/api';
import * as history from 'modules/history';
import * as notification from 'core/notification';

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


export function addComment(
    entity: number,
    locale: string,
    pluralForm: number,
    translation?: number,
    comment: string,
): Function {
    return async dispatch => {
        NProgress.start();

        await api.comment.add(entity, locale, comment, translation);

        dispatch(notification.actions.add(notification.messages.COMMENT_ADDED));
        if (translation) {
            dispatch(history.actions.get(entity, locale, pluralForm));
        }
        else {
            dispatch(get(entity, locale));
        }

        NProgress.done();
    }
}


export default {
    get,
    receive,
    request,
    addComment,
};
