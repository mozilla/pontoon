/* @flow */

import { UPDATE, UPDATE_SELECTION } from './actions';

import type { UpdateAction, UpdateSelectionAction } from './actions';


type Action =
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
        default:
            return state;
    }
}
