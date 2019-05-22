/* @flow */

import { RECEIVE, UPDATE } from './actions';

import type { Resource, ReceiveAction, UpdateAction } from './actions';


type Action =
    | ReceiveAction
    | UpdateAction
;

export type ResourcesState = {|
    +resources: Array<Resource>,
|};


function updateResource(
    state: Object,
    resource_path: string,
    approved_strings: number,
    strings_with_warnings: number,
): Array<Resource> {
    return state.resources.map(item => {
        if (item.path === resource_path) {
            const allResources = state.resources.slice(-1)[0];

            const diff_approved = approved_strings - item.approved_strings;
            item.approved_strings += diff_approved;
            allResources.approved_strings += diff_approved;

            const diff_warnings = strings_with_warnings - item.strings_with_warnings;
            item.strings_with_warnings += diff_warnings;
            allResources.strings_with_warnings += diff_warnings;
        }

        return item;
    });
}


const initial: ResourcesState = {
    resources: [],
};

export default function reducer(
    state: ResourcesState = initial,
    action: Action,
): ResourcesState {
    switch (action.type) {
        case RECEIVE:
            return {
                ...state,
                resources: action.resources,
            };
        case UPDATE:
            return {
                ...state,
                resources: updateResource(
                    state,
                    action.resource_path,
                    action.approved_strings,
                    action.strings_with_warnings,
                ),
            };
        default:
            return state;
    }
}
