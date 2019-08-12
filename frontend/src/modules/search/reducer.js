/* @flow */

import { UPDATE } from './actions';

import type { Author, UpdateAction } from './actions';


type Action =
    | UpdateAction
;

export type AuthorsAndTimeRangeState = {|
    +authors: Array<Author>,
    +countsPerMinute: Array<Array<number>>,
|};


const initial: AuthorsAndTimeRangeState = {
    authors: [],
    countsPerMinute: [],
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
        default:
            return state;
    }
}
