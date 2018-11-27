/* @flow */

import { RECEIVE, REQUEST, UPDATE } from './actions';
import type { ReceiveAction, RequestAction, UpdateAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
    | UpdateAction
;


export type DBTranslation = {|
    +approved: boolean,
    +approved_user: string,
    +date: string,
    +date_iso: string,
    +fuzzy: boolean,
    +pk: number,
    +rejected: boolean,
    +string: string,
    +uid: ?number,
    +unapproved_user: string,
    +user: string,
    +username: string,
|};

export type HistoryState = {|
    +fetching: boolean,
    +translations: Array<DBTranslation>,
|};


function updateTranslation(translations: Array<DBTranslation>, newTranslation: DBTranslation) {
    return translations.map(translation => {
        if (translation.pk === newTranslation.pk) {
            return { ...translation, ...newTranslation };
        }
        return translation;
    });
}


const initialState = {
    fetching: false,
    translations: [],
};

export default function reducer(
    state: HistoryState = initialState,
    action: Action
): HistoryState {
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
        case UPDATE:
            return {
                ...state,
                translations: updateTranslation(state.translations, action.translation),
            };
        default:
            return state;
    }
}
