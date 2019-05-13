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
    +exist: boolean,
    +callback: ?Function,
    +ignored: boolean,
|};


const initialState = {
    exist: false,
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
                exist: true,
                callback: action.callback,
            };
        case HIDE:
            return {
                ...state,
                exist: false,
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
