/* @flow */

import { RECEIVE, REQUEST } from './actions';

import type { TeamComment } from 'core/api';
import type { ReceiveAction, RequestAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
;


export type TeamCommentState = {|
    +fetching: boolean,
    +entity: ?number,
    +comments: Array<TeamComment>,
|};


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
        default:
            return state;
    }
}
