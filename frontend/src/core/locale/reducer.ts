import { RECEIVE, REQUEST } from './actions';

import type { Locale, ReceiveAction, RequestAction } from './actions';

type Action = ReceiveAction | RequestAction;

export type LocaleState = Locale & {
    readonly fetching: boolean;
};

const initial: LocaleState = {
    code: '',
    name: '',
    cldrPlurals: [],
    pluralRule: '',
    direction: '',
    script: '',
    googleTranslateCode: '',
    msTranslatorCode: '',
    systranTranslateCode: '',
    msTerminologyCode: '',
    localizations: [],
    fetching: false,
};

export default function reducer(
    state: LocaleState = initial,
    action: Action,
): LocaleState {
    switch (action.type) {
        case RECEIVE:
            return {
                ...state,
                ...action.locale,
                fetching: false,
            };
        case REQUEST:
            return {
                ...state,
                fetching: true,
            };
        default:
            return state;
    }
}
