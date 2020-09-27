/* @flow */

import { HIDE, IGNORE, SHOW, UPDATE } from './actions';

import type {
    HideAction,
    IgnoreAction,
    ShowAction,
    UpdateAction,
} from './actions';

type Action = HideAction | IgnoreAction | ShowAction | UpdateAction;

export type UnsavedChangesState = {|
    +callback: ?Function,
    +exist: boolean,
    +ignored: boolean,
    +shown: boolean,
|};

const initialState = {
    callback: null,
    exist: false,
    ignored: false,
    shown: false,
};

export default function reducer(
    state: UnsavedChangesState = initialState,
    action: Action,
): UnsavedChangesState {
    switch (action.type) {
        case HIDE:
            return {
                ...state,
                callback: null,
                exist: false,
                ignored: false,
                shown: false,
            };
        case IGNORE:
            return {
                ...state,
                ignored: true,
            };
        case SHOW:
            return {
                ...state,
                shown: true,
                callback: action.callback,
            };
        case UPDATE:
            return {
                ...state,
                exist: action.exist,
                ignored: false,
            };
        default:
            return state;
    }
}
