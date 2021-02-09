import { RECEIVE, REQUEST, UPDATE } from './actions';

import { ReceiveAction, RequestAction, UpdateAction } from './actions';
import { TranslationComment } from 'core/api';

type Action = ReceiveAction | RequestAction | UpdateAction;

export type HistoryTranslation = {
    readonly approved: boolean;
    readonly approvedUser: string;
    readonly date: string;
    readonly dateIso: string;
    readonly fuzzy: boolean;
    readonly pk: number;
    readonly rejected: boolean;
    readonly string: string;
    readonly uid: number | null | undefined;
    readonly unapprovedUser: string;
    readonly machinerySources: string;
    readonly user: string;
    readonly username: string;
    readonly userGravatarUrlSmall: string;
    readonly comments: Array<TranslationComment>;
};

export type HistoryState = {
    readonly fetching: boolean;
    readonly entity: number | null | undefined;
    readonly pluralForm: number | null | undefined;
    readonly translations: Array<HistoryTranslation>;
};

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
