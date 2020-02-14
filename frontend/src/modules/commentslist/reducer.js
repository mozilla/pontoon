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
    +comments: Array<TeamComment>,
|};


const initialState = {
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
                entity: action.entity,
                comments: [],
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
