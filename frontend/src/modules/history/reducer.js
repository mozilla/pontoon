/* @flow */

import { INVALIDATE, RECEIVE, REQUEST } from './actions';
import type { InvalidateAction, ReceiveAction, RequestAction } from './actions';


type Action =
    | InvalidateAction
    | ReceiveAction
    | RequestAction
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
    +didInvalidate: boolean,
    +translations: Array<DBTranslation>,
|};


const initialState = {
    fetching: false,
    didInvalidate: true,
    translations: [],
};

export default function reducer(
    state: HistoryState = initialState,
    action: Action
): HistoryState {
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
