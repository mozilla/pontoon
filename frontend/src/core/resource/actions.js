/* @flow */

import api from 'core/api';


export const RECEIVE: 'resource/RECEIVE' = 'resource/RECEIVE';
export const REQUEST: 'resource/REQUEST' = 'resource/REQUEST';


export type Resource = {|
    +path: string,
    +approved_strings: number,
    +total_strings: number,
|};


export type RequestAction = {|
    type: typeof REQUEST,
|};
export function request() {
    return {
        type: REQUEST,
    };
}


export type ReceiveAction = {|
    type: typeof RECEIVE,
    resources: Array<Resource>,
|};
export function receive(resources: Array<Resource>) {
    return {
        type: RECEIVE,
        resources,
    };
}


export function get(locale: string, project: string): Function {
    return async dispatch => {
        dispatch(request());

        const results = await api.resource.getAll(locale, project);

        const resources = results.map(resource => {
            return {
                path: resource.resource__path,
                approved_strings: resource.approved_strings,
                total_strings: resource.resource__total_strings,
            };
        });

        dispatch(receive(resources));
    }
}

export default {
    get,
};
