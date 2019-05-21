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
    resource: Resource,
): Array<Resource> {
    return state.resources.map(item => {
        if (item.path === resource.path) {
            return resource;
        }
        else {
            return item;
        }
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
                    action.resource,
                ),
            };
        default:
            return state;
    }
}
