import isEmpty from 'lodash.isempty';

import api from 'core/api';

import type { TeamComment } from 'core/api';

export const RECEIVE: 'comments/RECEIVE' = 'comments/RECEIVE';
export const REQUEST: 'comments/REQUEST' = 'comments/REQUEST';
export const TOGGLE_PINNED: 'comments/TOGGLE_PINNED' = 'comments/TOGGLE_PINNED';

export type ReceiveAction = {
    readonly type: typeof RECEIVE;
    readonly comments: Array<TeamComment>;
};
export function receive(comments: Array<TeamComment>): ReceiveAction {
    return {
        type: RECEIVE,
        comments,
    };
}

export type RequestAction = {
    readonly type: typeof REQUEST;
    readonly entity: number;
};
export function request(entity: number): RequestAction {
    return {
        type: REQUEST,
        entity,
    };
}

export type TogglePinnedAction = {
    readonly type: typeof TOGGLE_PINNED;
    readonly pinned: boolean;
    readonly commentId: number;
};
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

export function get(
    entity: number,
    locale: string,
): (...args: Array<any>) => any {
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
): (...args: Array<any>) => any {
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
