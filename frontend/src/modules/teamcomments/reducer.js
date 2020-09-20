/* @flow */

import { RECEIVE, REQUEST, UPDATE_PINNED } from './actions';

import type { TeamComment } from 'core/api';
import type { ReceiveAction, RequestAction, UpdatePinnedAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
    | UpdatePinnedAction
;


export type TeamCommentState = {|
    +fetching: boolean,
    +entity: ?number,
    +comments: Array<TeamComment>,
|};

function updatePinnedComment(
    state: Object,
    pinned: boolean,
    commentId: number,
): Array<TeamComment> {
    return state.comments.map(comment => {
        if (comment.id !== commentId) {
            return comment;
        }

        comment.pinned = pinned;

        return {
            ...comment,
        };
    });
}


const initialState = {
    fetching: false,
    entity: null,
    comments: [],
};

export default function reducer(
    state: TeamCommentState = initialState,
    action: Action
): TeamCommentState {
    switch (action.type) {
        case REQUEST:
            return {
                ...state,
                fetching: true,
                entity: action.entity,
                comments: [],
            };
        case RECEIVE:
            return {
                ...state,
                fetching: false,
                comments: action.comments,
            };
        case UPDATE_PINNED:
            return {
                ...state,
                comments: updatePinnedComment(
                    state,
                    action.pinned,
                    action.commentId,
                )
            }
        default:
            return state;
    }
}
