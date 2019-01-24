/* @flow */

import api from 'core/api';

import { ADD_TRANSLATIONS, RESET } from './actions';

import type { AddTranslationsAction, ResetAction } from './actions';


type Action =
    | AddTranslationsAction
    | ResetAction
;

export type MachineryState = {|
    translations: Array<api.types.MachineryTranslation>,
|};


const initial: MachineryState = {
    translations: [],
};

export default function reducer(
    state: MachineryState = initial,
    action: Action,
): MachineryState {
    switch (action.type) {
        case ADD_TRANSLATIONS:
            return {
                ...state,
                translations: [
                    ...state.translations,
                    ...action.translations,
                ],
            };
        case RESET:
            return {
                ...state,
                translations: [],
            };
        default:
            return state;
    }
}
