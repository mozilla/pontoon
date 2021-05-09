/* @flow */

import { UPDATE, SET_FOCUS } from './actions';

import type { Author, UpdateAction, SetFocusAction } from './actions';

type Action = UpdateAction | SetFocusAction;

export type SearchAndFilters = {|
    +authors: Array<Author>,
    +countsPerMinute: Array<Array<number>>,
    +searchInputFocused: boolean,
|};

const initial: SearchAndFilters = {
    authors: [],
    countsPerMinute: [],
    searchInputFocused: false,
};

export default function reducer(
    state: SearchAndFilters = initial,
    action: Action,
): SearchAndFilters {
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
