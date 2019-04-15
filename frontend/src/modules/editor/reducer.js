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
    +selectionReplacementContent: string,
|};


const initial: EditorState = {
    translation: '',
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
            };
        case UPDATE_SELECTION:
            return {
                ...state,
                selectionReplacementContent: action.content,
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
