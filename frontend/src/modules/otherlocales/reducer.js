/* @flow */

import { RECEIVE, REQUEST } from './actions';

import type { OtherLocaleTranslation } from 'core/api';
import type { ReceiveAction, RequestAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
;


export type LocalesState = {|
    +fetching: boolean,
    +entity: ?number,
    +translations: Array<OtherLocaleTranslation>,
|};


const initialState = {
    fetching: false,
    entity: null,
    translations: [],
};

export default function reducer(
    state: LocalesState = initialState,
    action: Action
): LocalesState {
    switch (action.type) {
        case REQUEST:
            return {
                ...state,
                fetching: true,
                entity: null,
                translations: [],
            };
        case RECEIVE:
            return {
                ...state,
                fetching: false,
                entity: action.entity,
                translations: action.translations,
            };
        default:
            return state;
    }
}
