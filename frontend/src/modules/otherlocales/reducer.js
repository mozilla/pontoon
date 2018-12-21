/* @flow */

import api from 'core/api';

import { RECEIVE, REQUEST } from './actions';
import type { ReceiveAction, RequestAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
;


export type LocalesState = {|
    +fetching: boolean,
    +translations: Array<api.types.OtherLocaleTranslation>,
|};


const initialState = {
    fetching: false,
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
