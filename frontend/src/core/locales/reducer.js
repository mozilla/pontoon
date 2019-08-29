/* @flow */

import { RECEIVE, REQUEST } from './actions';

import type { Locale, ReceiveAction, RequestAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
;

export type LocalesState = {|
    ...Locale,
    +fetching: boolean,
|};


const initial: LocalesState = {
    code: '',
    name: '',
    cldrPlurals: [],
    pluralRule: '',
    direction: '',
    script: '',
    googleTranslateCode: '',
    msTranslatorCode: '',
    msTerminologyCode: '',
    transvision: false,
    fetching: false,
};

export default function reducer(
    state: LocalesState = initial,
    action: Action,
): LocalesState {
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
