/* @flow */

import { RECEIVE, REQUEST, UPDATE } from './actions';

import type { ReceiveAction, RequestAction, UpdateAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
    | UpdateAction
;


export type HistoryTranslation = {|
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
    +user_gravatar_url_small: string,
|};

export type HistoryState = {|
    +fetching: boolean,
    +entity: ?number,
    +pluralForm: ?number,
    +translations: Array<HistoryTranslation>,
|};


function updateTranslation(translations: Array<HistoryTranslation>, newTranslation: HistoryTranslation) {
    return translations.map(translation => {
        if (translation.pk === newTranslation.pk) {
            return { ...translation, ...newTranslation };
        }
        return translation;
    });
}


const initialState = {
    fetching: false,
    entity: null,
    pluralForm: null,
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
                entity: action.entity,
                pluralForm: action.pluralForm,
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
