/* @flow */

import { RECEIVE, REQUEST, UPDATE } from './actions';

import type { ReceiveAction, RequestAction, UpdateAction } from './actions';
import type { TranslationComment } from 'core/api';

type Action = ReceiveAction | RequestAction | UpdateAction;

export type HistoryTranslation = {|
    +approved: boolean,
    +approvedUser: string,
    +date: string,
    +dateIso: string,
    +fuzzy: boolean,
    +pk: number,
    +rejected: boolean,
    +string: string,
    +uid: ?number,
    +unapprovedUser: string,
    +machinerySources: string,
    +user: string,
    +username: string,
    +userGravatarUrlSmall: string,
    +comments: Array<TranslationComment>,
|};

export type HistoryState = {|
    +fetching: boolean,
    +entity: ?number,
    +pluralForm: ?number,
    +translations: Array<HistoryTranslation>,
|};

function updateTranslation(
    translations: Array<HistoryTranslation>,
    newTranslation: HistoryTranslation,
) {
    return translations.map((translation) => {
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
    action: Action,
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
                translations: updateTranslation(
                    state.translations,
                    action.translation,
                ),
            };
        default:
            return state;
    }
}
