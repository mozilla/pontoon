import { LOCATION_CHANGE } from 'connected-react-router';
import type { LocationChangeAction } from 'connected-react-router';

import { RESET, SELECT } from './actions';

import type { ResetAction, SelectAction } from './actions';

type Action = LocationChangeAction | ResetAction | SelectAction;

export type PluralState = {
    readonly pluralForm: number;
};

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
        case LOCATION_CHANGE:
        case RESET:
            return {
                ...initial,
            };
        default:
            return state;
    }
}
