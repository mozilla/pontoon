/* @flow */

import { RECEIVE } from './actions';

import type { ReceiveAction } from './actions';


type Action =
    | ReceiveAction
;


export type CommentState = {|
    +users: Array<Object>,
|};

const initialState = {
    users: [],
};

export default function reducer(
    state: CommentState = initialState,
    action: Action
): CommentState {
    switch (action.type) {
        case RECEIVE:
            return {
                ...state,
                users: action.users,
            };
        default:
            return state;
    }
}