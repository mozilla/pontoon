/* @flow */

import isEmpty from 'lodash.isempty';

import api from 'core/api';

import type { TeamComment } from 'core/api';

export const RECEIVE: 'comments/RECEIVE' = 'comments/RECEIVE';
export const REQUEST: 'comments/REQUEST' = 'comments/REQUEST';
export const TOGGLE_PINNED: 'comments/TOGGLE_PINNED' = 'comments/TOGGLE_PINNED';

export type ReceiveAction = {|
    +type: typeof RECEIVE,
    +comments: Array<TeamComment>,
|};
export function receive(comments: Array<TeamComment>): ReceiveAction {
    return {
        type: RECEIVE,
        comments,
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

export type TogglePinnedAction = {|
    +type: typeof TOGGLE_PINNED,
    +pinned: boolean,
    +commentId: number,
|};
export function togglePinned(
    pinned: boolean,
    commentId: number,
): TogglePinnedAction {
    return {
        type: TOGGLE_PINNED,
        pinned,
        commentId,
    };
}

export function get(entity: number, locale: string): Function {
    return async (dispatch) => {
        // request() must be called separately to prevent
        // re-rendering of the component on addComment()

        // Abort all previously running requests.
        await api.entity.abort();

        let content = await api.entity.getTeamComments(entity, locale);

        // The default return value of aborted requests is {},
        // which is incompatible with reducer
        if (isEmpty(content)) {
            content = [];
        }

        dispatch(receive(content));
    };
}

export function togglePinnedStatus(
    pinned: boolean,
    commentId: number,
): Function {
    return async (dispatch) => {
        if (pinned) {
            await api.comment.pinComment(commentId);
        } else {
            await api.comment.unpinComment(commentId);
        }

        dispatch(togglePinned(pinned, commentId));
    };
}

export default {
    get,
    receive,
    request,
    togglePinnedStatus,
};
