/* @flow */

import {
    HIDE,
    IGNORE,
    SHOW,
} from './actions';

import type {
    HideAction,
    IgnoreAction,
    ShowAction,
} from './actions';


type Action =
    | HideAction
    | IgnoreAction
    | ShowAction
;


export type UnsavedChangesState = {|
    +shown: boolean,
    +callback: ?Function,
    +ignored: boolean,
|};


const initialState = {
    shown: false,
    callback: null,
    ignored: false,
};

export default function reducer(
    state: UnsavedChangesState = initialState,
    action: Action,
): UnsavedChangesState {
    switch (action.type) {
        case SHOW:
            return {
                ...state,
                shown: true,
                callback: action.callback,
            };
        case HIDE:
            return {
                ...state,
                shown: false,
                callback: null,
                ignored: false,
            };
        case IGNORE:
            return {
                ...state,
                ignored: true,
            };
        default:
            return state;
    }
}
