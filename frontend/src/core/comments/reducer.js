/* @flow */

import { RECEIVE, REQUEST } from './actions';

import type { TeamComment } from 'core/api';
import type { ReceiveAction, RequestAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
;


export type TeamCommentState = {|
    +entity: ?number,
    +comments: ?TeamComment,
|};


const initialState = {
    entity: null,
    comments: null,
};

export default function reducer(
    state: TeamCommentState = initialState,
    action: Action
): TeamCommentState {
    switch (action.type) {
        case REQUEST:
            return {
                ...state,
                entity: action.entity,
                comments: null,
            };
        case RECEIVE:
            return {
                ...state,
                comments: action.comments,
            };
        default:
            return state;
    }
}
