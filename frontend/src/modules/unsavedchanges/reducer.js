/* @flow */

import {
    HIDE_UNSAVED_CHANGES,
    IGNORE_UNSAVED_CHANGES,
    SHOW_UNSAVED_CHANGES,
} from './actions';

import type {
    HideUnsavedChangesAction,
    IgnoreUnsavedChangesAction,
    ShowUnsavedChangesAction,
} from './actions';


type Action =
    | HideUnsavedChangesAction
    | IgnoreUnsavedChangesAction
    | ShowUnsavedChangesAction
;


export type UnsavedChangesState = {|
    +unsavedChanges: boolean,
    +unsavedChangesCallback: Function,
    +unsavedChangesIgnored: boolean,
|};


const initialState = {
    unsavedChanges: false,
    unsavedChangesCallback: null,
    unsavedChangesIgnored: false,
};

export default function reducer(
    state: UnsavedChangesState = initialState,
    action: Action,
): UnsavedChangesState {
    switch (action.type) {
        case SHOW_UNSAVED_CHANGES:
            return {
                ...state,
                unsavedChanges: true,
                unsavedChangesCallback: action.unsavedChangesCallback,
            };
        case HIDE_UNSAVED_CHANGES:
            return {
                ...state,
                unsavedChanges: false,
                unsavedChangesCallback: null,
                unsavedChangesIgnored: false,
            };
        case IGNORE_UNSAVED_CHANGES:
            return {
                ...state,
                unsavedChangesIgnored: true,
            };
        default:
            return state;
    }
}
