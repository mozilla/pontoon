/* @flow */

import api from 'core/api';

export const RECEIVE: 'resource/RECEIVE' = 'resource/RECEIVE';
export const UPDATE: 'resource/UPDATE' = 'resource/UPDATE';

export type Resource = {|
    +path: string,
    +approvedStrings: number,
    +stringsWithWarnings: number,
    +totalStrings: number,
|};

export type UpdateAction = {|
    type: typeof UPDATE,
    resourcePath: string,
    approvedStrings: number,
    stringsWithWarnings: number,
|};
export function update(
    resourcePath: string,
    approvedStrings: number,
    stringsWithWarnings: number,
): UpdateAction {
    return {
        type: UPDATE,
        resourcePath,
        approvedStrings,
        stringsWithWarnings,
    };
}

export type ReceiveAction = {|
    type: typeof RECEIVE,
    resources: Array<Resource>,
    allResources: Resource,
|};
export function receive(
    resources: Array<Resource>,
    allResources: Resource,
): ReceiveAction {
    return {
        type: RECEIVE,
        resources,
        allResources,
    };
}

export function get(locale: string, project: string): Function {
    return async (dispatch) => {
        const results = await api.resource.getAll(locale, project);

        const resources = results.map((resource) => {
            return {
                path: resource.title,
                approvedStrings: resource.approved_strings,
                stringsWithWarnings: resource.strings_with_warnings,
                totalStrings: resource.resource__total_strings,
            };
        });

        const allResources = resources.pop();

        dispatch(receive(resources, allResources));
    };
}

export default {
    get,
    update,
};
