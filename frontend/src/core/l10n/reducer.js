/* @flow */

import { ReactLocalization } from '@fluent/react';

import { RECEIVE, REQUEST } from './actions';

import type { ReceiveAction, RequestAction } from './actions';

type Action = ReceiveAction | RequestAction;

export type L10nState = {|
    +fetching: boolean,
    +localization: ReactLocalization,
|};

const initial: L10nState = {
    fetching: false,
    localization: new ReactLocalization([]),
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
                localization: action.localization,
            };
        default:
            return state;
    }
}
