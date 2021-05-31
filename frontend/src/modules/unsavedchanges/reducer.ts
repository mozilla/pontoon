import { HIDE, IGNORE, SHOW, UPDATE } from './actions';

import type {
    HideAction,
    IgnoreAction,
    ShowAction,
    UpdateAction,
} from './actions';

type Action = HideAction | IgnoreAction | ShowAction | UpdateAction;

export type UnsavedChangesState = {
    readonly callback: ((...args: Array<any>) => any) | null | undefined;
    readonly exist: boolean;
    readonly ignored: boolean;
    readonly shown: boolean;
};

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
