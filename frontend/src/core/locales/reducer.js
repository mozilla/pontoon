/* @flow */

import { RECEIVE, REQUEST } from './actions';

import type { Locale, ReceiveAction, RequestAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
;

export type LocalesState = {|
    +fetching: boolean,
    +locales: { [string]: Locale },
|};


const initial: LocalesState = {
    fetching: false,
    locales: {},
};

export default function reducer(
    state: LocalesState = initial,
    action: Action,
): LocalesState {
    switch (action.type) {
        case RECEIVE:
            return {
                ...state,
                fetching: false,
                locales: action.locales,
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
