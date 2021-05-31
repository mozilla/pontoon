import { RECEIVE, UPDATE } from './actions';

import type { Resource, ReceiveAction, UpdateAction } from './actions';

type Action = ReceiveAction | UpdateAction;

export type ResourcesState = {
    readonly resources: Array<Resource>;
    readonly allResources: Resource;
};

function updateResource(
    resources: Array<Resource>,
    resourcePath: string,
    approvedStrings: number,
    stringsWithWarnings: number,
): Array<Resource> {
    return resources.map((item) => {
        if (item.path === resourcePath) {
            return {
                ...item,
                approvedStrings,
                stringsWithWarnings,
            };
        } else {
            return item;
        }
    });
}

function updateAllResources(
    state: Record<string, any>,
    resourcePath: string,
    approvedStrings: number,
    stringsWithWarnings: number,
): Resource {
    const updatedResource = state.resources.find(
        (item) => item.path === resourcePath,
    );

    // That can happen in All Projects view
    if (!updatedResource) {
        return state.allResources;
    }

    const diffApproved = approvedStrings - updatedResource.approvedStrings;
    const diffWarnings =
        stringsWithWarnings - updatedResource.stringsWithWarnings;

    return {
        ...state.allResources,
        approvedStrings: state.allResources.approvedStrings + diffApproved,
        stringsWithWarnings:
            state.allResources.stringsWithWarnings + diffWarnings,
    };
}

const initial: ResourcesState = {
    resources: [],
    allResources: {
        path: 'all-resources',
        approvedStrings: 0,
        stringsWithWarnings: 0,
        totalStrings: 0,
    },
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
                allResources: action.allResources,
            };
        case UPDATE:
            return {
                ...state,
                resources: updateResource(
                    state.resources,
                    action.resourcePath,
                    action.approvedStrings,
                    action.stringsWithWarnings,
                ),
                allResources: updateAllResources(
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
