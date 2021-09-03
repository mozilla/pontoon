import { RECEIVE, REQUEST } from './actions';

import type { ReceiveAction, RequestAction, Tag } from './actions';

type Action = ReceiveAction | RequestAction;

export type ProjectState = {
    readonly fetching: boolean;
    readonly slug: string;
    readonly name: string;
    readonly info: string;
    readonly tags: Array<Tag>;
};

const initial: ProjectState = {
    fetching: false,
    slug: '',
    name: '',
    info: '',
    tags: [],
};

export default function reducer(
    state: ProjectState = initial,
    action: Action,
): ProjectState {
    switch (action.type) {
        case REQUEST:
            return {
                ...state,
                fetching: true,
            };
        case RECEIVE:
            return {
                ...state,
                fetching: false,
                slug: action.slug,
                name: action.name,
                info: action.info,
                tags: action.tags,
            };
        default:
            return state;
    }
}
