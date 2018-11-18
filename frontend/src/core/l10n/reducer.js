/* @flow */

import { FluentBundle } from 'fluent';

import { RECEIVE, REQUEST } from './actions';
import type { ReceiveAction, RequestAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
;

export type L10nState = {|
    +fetching: boolean,
    +bundles: Array<FluentBundle>,
|};


const initial: L10nState = {
    fetching: false,
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
        default:
            return state;
    }
}
