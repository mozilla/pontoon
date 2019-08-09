/* @flow */

import { RECEIVE, REQUEST } from './actions';

import type { Author, ReceiveAction, RequestAction } from './actions';


type Action =
    | ReceiveAction
    | RequestAction
;

export type AuthorsAndTimeRangeState = {|
    +fetching: boolean,
    +authors: Array<Author>,
    +countsPerMinute: Array<Array<number>>,
|};


const initial: AuthorsAndTimeRangeState = {
    fetching: false,
    authors: [],
    countsPerMinute: [],
};

export default function reducer(
    state: AuthorsAndTimeRangeState = initial,
    action: Action,
): AuthorsAndTimeRangeState {
    switch (action.type) {
        case RECEIVE:
            return {
                ...state,
                fetching: false,
                authors: action.response.authors,
                countsPerMinute: action.response.counts_per_minute,
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
