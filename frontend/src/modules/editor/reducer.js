/* @flow */

import { RESET_SELECTION, UPDATE, UPDATE_SELECTION } from './actions';

import type {
    ResetSelectionAction,
    UpdateAction,
    UpdateSelectionAction,
} from './actions';


type Action =
    | ResetSelectionAction
    | UpdateAction
    | UpdateSelectionAction
;

export type EditorState = {|
    +translation: string,
    +changeSource: string,
    +selectionReplacementContent: string,
|};


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
        case UPDATE_SELECTION:
            return {
                ...state,
                selectionReplacementContent: action.content,
                changeSource: 'internal',
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
