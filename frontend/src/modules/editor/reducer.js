/* @flow */

import { UPDATE } from './actions';

import type { UpdateAction } from './actions';


type Action =
    | UpdateAction
;

export type EditorState = {|
    +translation: string,
    +caretPosition: number,
|};


const initial: EditorState = {
    translation: '',
    caretPosition: 0,
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
        default:
            return state;
    }
}
