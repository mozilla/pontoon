/* @flow */

import { RECEIVE, REQUEST } from './actions';

import type { ReceiveAction, RequestAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
;


export type ProjectState = {|
    +fetching: boolean,
    +name: string,
    +info: string,
|};


const initial: ProjectState = {
    fetching: false,
    name: '',
    info: '',
};

export default function reducer(
    state: ProjectState = initial,
    action: Action,
): ProjectState {
    switch (action.type) {
        case REQUEST:
            return {
                ...state,
                fetching: true,
            };
        case RECEIVE:
            return {
                ...state,
                fetching: false,
                name: action.name,
                info: action.info,
            };
        default:
            return state;
    }
}
