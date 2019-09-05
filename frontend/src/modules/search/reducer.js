/* @flow */

import { UPDATE, SET_FOCUS } from './actions';

import type { Author, UpdateAction } from './actions';


type Action =
    | UpdateAction
;

export type AuthorsAndTimeRangeState = {|
    +authors: Array<Author>,
    +countsPerMinute: Array<Array<number>>,
    +searchInputFocused: boolean,
|};


const initial: AuthorsAndTimeRangeState = {
    authors: [],
    countsPerMinute: [],
    searchInputFocused: false,
};

export default function reducer(
    state: AuthorsAndTimeRangeState = initial,
    action: Action,
): AuthorsAndTimeRangeState {
    switch (action.type) {
        case UPDATE:
            return {
                ...state,
                authors: action.response.authors,
                countsPerMinute: action.response.counts_per_minute,
            };
        case SET_FOCUS:
            return {
                ...state,
                searchInputFocused: action.searchInputFocused,
            };
        default:
            return state;
    }
}
