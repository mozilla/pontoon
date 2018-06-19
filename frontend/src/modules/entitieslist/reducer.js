/* @flow */

import { RECEIVE, REQUEST } from './actions';
import type { ReceiveAction, RequestAction } from './actions';


export type Action =
    | ReceiveAction
    | RequestAction
;

export type Entities = Array<Object>;
export type State = {
    +entities: Entities,
    +fetching: boolean,
    +errors: Array<string>,
};


const initial: State = {
    entities: [],
    fetching: false,
    errors: [],
};

export default function reducer(state: State = initial, action: Action): State {
    switch (action.type) {
        case RECEIVE:
            return { ...state, ...{
                entities: action.entities,
                fetching: false,
            } };
        case REQUEST:
            return { ...state, ...{ fetching: true } };
        default:
            return state;
    }
}
