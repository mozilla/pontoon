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
    +entity: ?number,
    +fetching: boolean,
    +translations: Array<DBTranslation>,
|};


const initialState = {
    entity: null,
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
                entity: action.entity,
                fetching: true,
                translations: [],
            };
        case RECEIVE:
            if (action.entity !== state.entity) {
                // The selected entity changed since the request was sent,
                // those results are not pertinent anymore. Do nothing.
                return state;
            }

            return {
                ...state,
                fetching: false,
                translations: action.translations,
            };
        default:
            return state;
    }
}
