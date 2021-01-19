/* @flow */

import { RECEIVE, REQUEST } from './actions';

import type { OtherLocaleTranslations } from 'core/api';
import type { ReceiveAction, RequestAction } from './actions';

type Action = ReceiveAction | RequestAction;

export type LocalesState = {|
    +fetching: boolean,
    +entity: ?number,
    +translations: OtherLocaleTranslations,
|};

const initialState = {
    fetching: false,
    entity: null,
    translations: [],
};

export default function reducer(
    state: LocalesState = initialState,
    action: Action,
): LocalesState {
    switch (action.type) {
        case REQUEST:
            return {
                ...state,
                fetching: true,
                entity: action.entity,
                translations: [],
            };
        case RECEIVE:
            return {
                ...state,
                fetching: false,
                translations: action.translations,
            };
        default:
            return state;
    }
}
