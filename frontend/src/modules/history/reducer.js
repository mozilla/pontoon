/* @flow */

import { RECEIVE, REQUEST } from './actions';
import type { ReceiveAction, RequestAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
;


type Translation = {|
    pk: number,
    string: string,
    user: string,
    date_iso: string,
    fuzzy: boolean,
    approved: boolean,
    rejected: boolean,
|};

export type HistoryState = {|
    +entity: ?number,
    +fetching: boolean,
    +translations: Array<Translation>
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
                ...{ entity: action.entity, fetching: true },
            };
        case RECEIVE:
            if (action.entity !== state.entity) {
                // The selected entity changed since the request was sent,
                // those results are not pertinent anymore. Do nothing.
                return state;
            }

            return {
                ...state,
                ...{
                    fetching: false,
                    translations: action.translations,
                },
            };
        default:
            return state;
    }
}
