/* @flow */

import api from 'core/api';


export const RECEIVE: 'resource/RECEIVE' = 'resource/RECEIVE';
export const UPDATE: 'resource/UPDATE' = 'resource/UPDATE';


export type Resource = {|
    +path: string,
    +approved_strings: number,
    +strings_with_warnings: number,
    +total_strings: number,
|};


export type UpdateAction = {|
    type: typeof UPDATE,
    resource_path: string,
    approved_strings: number,
    strings_with_warnings: number,
|};
export function update(
    resource_path: string,
    approved_strings: number,
    strings_with_warnings: number,
): UpdateAction {
    return {
        type: UPDATE,
        resource_path,
        approved_strings,
        strings_with_warnings,
    };
}


export type ReceiveAction = {|
    type: typeof RECEIVE,
    resources: Array<Resource>,
|};
export function receive(resources: Array<Resource>): ReceiveAction {
    return {
        type: RECEIVE,
        resources,
    };
}


export function get(locale: string, project: string): Function {
    return async dispatch => {
        const results = await api.resource.getAll(locale, project);

        const resources = results.map(resource => {
            return {
                path: resource.resource__path,
                approved_strings: resource.approved_strings,
                strings_with_warnings: resource.strings_with_warnings,
                total_strings: resource.resource__total_strings,
            };
        });

        dispatch(receive(resources));
    }
}

export default {
    get,
    update,
};
