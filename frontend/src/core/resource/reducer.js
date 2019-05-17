/* @flow */

import { RECEIVE, REQUEST } from './actions';

import type { Resource, ReceiveAction, RequestAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
;

export type ResourcesState = {|
    +fetching: boolean,
    +resources: Array<Resource>,
|};


const initial: ResourcesState = {
    fetching: false,
    resources: [],
};

export default function reducer(
    state: ResourcesState = initial,
    action: Action,
): ResourcesState {
    switch (action.type) {
        case RECEIVE:
            return {
                ...state,
                fetching: false,
                resources: action.resources,
            };
        case REQUEST:
            return {
                ...state,
                fetching: true,
            };
        default:
            return state;
    }
}
