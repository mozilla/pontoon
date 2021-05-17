/* @flow */

import { LOCATION_CHANGE } from 'connected-react-router';
// TODO: TypeScript
// import type { LocationChangeAction } from 'connected-react-router';

import { RESET, SELECT } from './actions';

import type { ResetAction, SelectAction } from './actions';

type Action = ResetAction | SelectAction;

export type PluralState = {|
    +pluralForm: number,
|};

const initial: PluralState = {
    pluralForm: -1,
};

export default function reducer(
    state: PluralState = initial,
    action: Action,
): PluralState {
    switch (action.type) {
        case SELECT:
            return {
                ...state,
                pluralForm: action.pluralForm,
            };
        // @ts-expect-error
        case LOCATION_CHANGE:
        case RESET:
            return {
                ...initial,
            };
        default:
            return state;
    }
}
