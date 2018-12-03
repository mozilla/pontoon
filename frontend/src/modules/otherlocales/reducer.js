/* @flow */

import api from 'core/api';

import { INVALIDATE, RECEIVE, REQUEST } from './actions';
import type { InvalidateAction, ReceiveAction, RequestAction } from './actions';


type Action =
    | InvalidateAction
    | ReceiveAction
    | RequestAction
;


export type LocalesState = {|
    +fetching: boolean,
    +didInvalidate: boolean,
    +translations: Array<api.types.OtherLocaleTranslation>,
|};


const initialState = {
    fetching: false,
    didInvalidate: true,
    translations: [],
};

export default function reducer(
    state: LocalesState = initialState,
    action: Action
): LocalesState {
    switch (action.type) {
        case INVALIDATE:
            return {
                ...state,
                didInvalidate: true,
            };
        case REQUEST:
            return {
                ...state,
                fetching: true,
                didInvalidate: false,
                translations: [],
            };
        case RECEIVE:
            return {
                ...state,
                fetching: false,
                didInvalidate: false,
                translations: action.translations,
            };
        default:
            return state;
    }
}
