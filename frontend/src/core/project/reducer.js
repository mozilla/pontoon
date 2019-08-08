/* @flow */

import { RECEIVE, REQUEST } from './actions';

import type { ReceiveAction, RequestAction, Tag } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
;


export type ProjectState = {|
    +fetching: boolean,
    +name: string,
    +info: string,
    +tags: Array<Tag>,
|};


const initial: ProjectState = {
    fetching: false,
    name: '',
    info: '',
    tags: [],
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
                tags: action.tags,
            };
        default:
            return state;
    }
}
