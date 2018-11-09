/* @flow */

import { FluentBundle } from 'fluent';

import { RECEIVE, REQUEST, SELECT_LOCALES } from './actions';
import type { ReceiveAction, RequestAction, SelectLocaleAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
    | SelectLocaleAction
;

export type L10nState = {|
    +fetching: boolean,
    +locales: Array<string>,
    +bundles: Array<FluentBundle>,
|};


const initial: L10nState = {
    fetching: false,
    locales: [],
    bundles: [],
};

export default function reducer(
    state: L10nState = initial,
    action: Action,
): L10nState {
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
                bundles: action.bundles,
            };
        case SELECT_LOCALES:
            return {
                ...state,
                locales: action.locales,
            };
        default:
            return state;
    }
}
