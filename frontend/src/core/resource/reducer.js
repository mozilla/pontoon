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
    resourcePath: string,
    approvedStrings: number,
    stringsWithWarnings: number,
): Array<Resource> {
    return state.resources.map(item => {
        if (item.path === resourcePath) {
            const allResources = state.resources.slice(-1)[0];

            const diffApproved = approvedStrings - item.approvedStrings;
            item.approvedStrings += diffApproved;
            allResources.approvedStrings += diffApproved;

            const diffWarnings = stringsWithWarnings - item.stringsWithWarnings;
            item.stringsWithWarnings += diffWarnings;
            allResources.stringsWithWarnings += diffWarnings;
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
                    action.resourcePath,
                    action.approvedStrings,
                    action.stringsWithWarnings,
                ),
            };
        default:
            return state;
    }
}
