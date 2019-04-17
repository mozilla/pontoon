/* @flow */

import {
    RESET_FAILED_CHECKS,
    RESET_SELECTION,
    UPDATE,
    UPDATE_FAILED_CHECKS,
    UPDATE_SELECTION,
} from './actions';

import type {
    FailedChecks,
    ResetFailedChecksAction,
    ResetSelectionAction,
    UpdateAction,
    UpdateFailedChecksAction,
    UpdateSelectionAction,
} from './actions';


type Action =
    | ResetFailedChecksAction
    | ResetSelectionAction
    | UpdateAction
    | UpdateFailedChecksAction
    | UpdateSelectionAction
;

export type EditorState = {|
    +translation: string,
    +changeSource: string,
    +selectionReplacementContent: string,
    +errors: Array<string>,
    +warnings: Array<string>,
    +source: '' | 'stored' | 'submitted' | 'approved',
|};


/**
 * Return a list of failed check messages of a given type.
 */
function extractFailedChecksOfType(
    failedChecks: FailedChecks,
    type: 'Errors' | 'Warnings',
): Array<string> {
    let extractedFailedChecks = [];
    const keys = Object.keys(failedChecks);

    for (const key of keys) {
        if (key.endsWith(type)) {
            for (const message of failedChecks[key]) {
                extractedFailedChecks.push(message);
            }
        }
    }

    return extractedFailedChecks;
}


const initial: EditorState = {
    translation: '',

    // Source of the current change. 'internal' or missing if from inside the
    // Editor, 'external' otherwise. This allows the Editor to behave
    // differently depending on the type of change.
    changeSource: 'internal',

    // Order to replace the currently selected text inside the Editor with
    // this content. This is reset after that change has been made. Because
    // we have different Editor implementations, we need to let those components
    // perform the actual replacement logic.
    selectionReplacementContent: '',
    errors: [],
    warnings: [],
    source: '',
};

export default function reducer(
    state: EditorState = initial,
    action: Action,
): EditorState {
    switch (action.type) {
        case UPDATE:
            return {
                ...state,
                translation: action.translation,
                changeSource: action.changeSource,
            };
        case UPDATE_FAILED_CHECKS:
            return {
                ...state,
                errors: extractFailedChecksOfType(action.failedChecks, 'Errors'),
                warnings: extractFailedChecksOfType(action.failedChecks, 'Warnings'),
                source: action.source,
            };
        case UPDATE_SELECTION:
            return {
                ...state,
                selectionReplacementContent: action.content,
                changeSource: 'internal',
            };
        case RESET_FAILED_CHECKS:
            return {
                ...state,
                errors: [],
                warnings: [],
            };
        case RESET_SELECTION:
            return {
                ...state,
                selectionReplacementContent: '',
            };
        default:
            return state;
    }
}
