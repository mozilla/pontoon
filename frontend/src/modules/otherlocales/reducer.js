/* @flow */

import { RECEIVE, REQUEST } from './actions';

import type { OtherLocaleTranslations } from 'core/api';
import type { ReceiveAction, RequestAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
;


export type LocalesState = {|
    +fetching: boolean,
    +entity: ?number,
<<<<<<< HEAD
    +translations: ?OtherLocaleTranslations
=======
    +translations: {
        preferred: Array<OtherLocaleTranslation>,
        other: Array<OtherLocaleTranslation>,
    }
>>>>>>> Initial progress to refactor frontend
|};


const initialState = {
    fetching: false,
    entity: null,
<<<<<<< HEAD
    translations: null,
=======
    translations: {},
>>>>>>> Initial progress to refactor frontend
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
                entity: action.entity,
<<<<<<< HEAD
                translations: null,
=======
                translations: {},
>>>>>>> Initial progress to refactor frontend
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
