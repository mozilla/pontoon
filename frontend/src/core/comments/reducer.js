/* @flow */

import { RECEIVE } from './actions';

import type { ReceiveAction } from './actions';
import type { UsersList } from 'core/api';


type Action =
    | ReceiveAction
;


export type CommentState = {|
    +users: Array<UsersList>,
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
