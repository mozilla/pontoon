/* @flow */
import type { SourceType } from 'core/api';

import {
    END_UPDATE_TRANSLATION,
    RESET_FAILED_CHECKS,
    RESET_SELECTION,
    RESET_EDITOR,
    RESET_HELPER_ELEMENT_INDEX,
    SELECT_HELPER_ELEMENT_INDEX,
    SELECT_HELPER_TAB_INDEX,
    SET_INITIAL_TRANSLATION,
    START_UPDATE_TRANSLATION,
    UPDATE,
    UPDATE_FAILED_CHECKS,
    UPDATE_SELECTION,
    UPDATE_MACHINERY_SOURCES,
} from './actions';

import type {
    FailedChecks,
    EndUpdateTranslationAction,
    InitialTranslationAction,
    ResetEditorAction,
    ResetHelperElementIndexAction,
    ResetFailedChecksAction,
    ResetSelectionAction,
    SelectHelperElementIndexAction,
    SelectHelperTabIndexAction,
    StartUpdateTranslationAction,
    Translation,
    UpdateAction,
    UpdateFailedChecksAction,
    UpdateSelectionAction,
    UpdateMachinerySourcesAction,
} from './actions';

type Action =
    | EndUpdateTranslationAction
    | InitialTranslationAction
    | ResetEditorAction
    | ResetHelperElementIndexAction
    | ResetFailedChecksAction
    | ResetSelectionAction
    | SelectHelperElementIndexAction
    | SelectHelperTabIndexAction
    | StartUpdateTranslationAction
    | UpdateAction
    | UpdateFailedChecksAction
    | UpdateSelectionAction
    | UpdateMachinerySourcesAction;

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

    +machinerySources: Array<SourceType>,

    +machineryTranslation: string,

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

    // True when there is a request to send a new translation running, false
    // otherwise. Used to prevent duplicate actions from users spamming their
    // keyboard or mouse.
    +isRunningRequest: boolean,

    // Index of selected item in the helpers box
    +selectedHelperElementIndex: number,
    // Index of selected tab in the helpers box. Assumes the following:
    //  0 -> Machinery
    //  1 -> Other Locales
    +selectedHelperTabIndex: number,
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
    changeSource: 'reset',
    machinerySources: [],
    machineryTranslation: '',
    selectionReplacementContent: '',
    errors: [],
    warnings: [],
    source: '',
    isRunningRequest: false,
    selectedHelperElementIndex: -1,
    selectedHelperTabIndex: 0,
};

export default function reducer(
    state: EditorState = initial,
    action: Action,
): EditorState {
    switch (action.type) {
        case END_UPDATE_TRANSLATION:
            return {
                ...state,
                isRunningRequest: false,
            };
        case UPDATE:
            return {
                ...state,
                translation: action.translation,
                changeSource: action.changeSource,
                source: '',
            };
        case UPDATE_FAILED_CHECKS:
            return {
                ...state,
                errors: extractFailedChecksOfType(
                    action.failedChecks,
                    'Errors',
                ),
                warnings: extractFailedChecksOfType(
                    action.failedChecks,
                    'Warnings',
                ),
                source: action.source,
            };
        case UPDATE_SELECTION:
            return {
                ...state,
                selectionReplacementContent: action.content,
                changeSource: action.changeSource,
            };
        case SET_INITIAL_TRANSLATION:
            return {
                ...state,
                initialTranslation: action.translation,
                machineryTranslation: '',
                machinerySources: [],
            };
        case START_UPDATE_TRANSLATION:
            return {
                ...state,
                isRunningRequest: true,
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
                changeSource: 'internal',
            };
        case RESET_EDITOR:
            return {
                ...initial,
                isRunningRequest: state.isRunningRequest,
                selectedHelperTabIndex: state.selectedHelperTabIndex,
            };
        case UPDATE_MACHINERY_SOURCES:
            return {
                ...state,
                machineryTranslation: action.machineryTranslation,
                machinerySources: action.machinerySources,
            };
        case RESET_HELPER_ELEMENT_INDEX:
            return {
                ...state,
                selectedHelperElementIndex: -1,
            };
        case SELECT_HELPER_ELEMENT_INDEX:
            return {
                ...state,
                selectedHelperElementIndex: action.index,
            };
        case SELECT_HELPER_TAB_INDEX:
            return {
                ...state,
                selectedHelperTabIndex: action.index,
            };
        default:
            return state;
    }
}
