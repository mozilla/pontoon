/* @flow */

import {
    RESET_FAILED_CHECKS,
    RESET_FOCUSED_OR_FIRST_FIELD,
    RESET_SELECTION,
    SET_INITIAL_TRANSLATION,
    UPDATE,
    UPDATE_FAILED_CHECKS,
    UPDATE_FOCUSED_OR_FIRST_FIELD,
    UPDATE_SELECTION,
} from './actions';

import type {
    FailedChecks,
    ResetFailedChecksAction,
    ResetFocusedOrFirstFieldAction,
    ResetSelectionAction,
    InitialTranslationAction,
    Translation,
    UpdateAction,
    UpdateFocusedOrFirstFieldAction,
    UpdateFailedChecksAction,
    UpdateSelectionAction,
} from './actions';


type Action =
    | ResetFailedChecksAction
    | ResetFocusedOrFirstFieldAction
    | ResetSelectionAction
    | InitialTranslationAction
    | UpdateAction
    | UpdateFocusedOrFirstFieldAction
    | UpdateFailedChecksAction
    | UpdateSelectionAction
;

export type EditorState = {|
    +translation: Translation,

    // Used for storing the initial translation in Fluent editor,
    // needed for detecting unsaved changes.
    +initialTranslation: Translation,

    // Source of the current change: 'internal' if from inside the Editor,
    // 'history', 'machinery', 'otherlocales' if copied from corresponding
    // Helper tab, 'external' otherwise. This allows the Editor to behave
    // differently depending on the type of change.
    +changeSource: string,

    // Order to replace the text in the focused or first field of the Rich Editor
    // with this content. This is reset after that change has been made. Because
    // we have different Editor implementations, we need to let those components
    // perform the actual replacement logic.
    +focusedOrFirstFieldContent: string,

    // Order to replace the currently selected text inside the Editor with
    // this content. This is reset after that change has been made. Because
    // we have different Editor implementations, we need to let those components
    // perform the actual replacement logic.
    +selectionReplacementContent: string,

    +errors: Array<string>,
    +warnings: Array<string>,

    // A source of failed checks (errors and warnings). Possible values:
    //   - '': no failed checks are displayed (default)
    //   - 'stored': failed checks of the translation stored in the DB
    //   - 'submitted': failed checks of the submitted translation
    //   - number (translationId): failed checks of the approved translation
    +source: '' | 'stored' | 'submitted' | number,
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
    initialTranslation: '',
    changeSource: 'internal',
    focusedOrFirstFieldContent: '',
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
        case UPDATE_FOCUSED_OR_FIRST_FIELD:
            return {
                ...state,
                focusedOrFirstFieldContent: action.content,
                changeSource: 'internal',
            };
        case UPDATE_SELECTION:
            return {
                ...state,
                selectionReplacementContent: action.content,
                changeSource: 'internal',
            };
        case SET_INITIAL_TRANSLATION:
            return {
                ...state,
                initialTranslation: action.translation,
            };
        case RESET_FAILED_CHECKS:
            return {
                ...state,
                errors: [],
                warnings: [],
            };
        case RESET_FOCUSED_OR_FIRST_FIELD:
            return {
                ...state,
                focusedOrFirstFieldContent: '',
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
