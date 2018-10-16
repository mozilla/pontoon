/* @flow */

import { RECEIVE, REQUEST } from './actions';
import type { ReceiveAction, RequestAction } from './actions';


type Action =
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
    +translations: Array<DBTranslation>,
|};


const initialState = {
    fetching: true,
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
        default:
            return state;
    }
}
