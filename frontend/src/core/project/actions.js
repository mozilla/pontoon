/* @flow */

import api from 'core/api';


export const RECEIVE: 'project/RECEIVE' = 'project/RECEIVE';
export const REQUEST: 'project/REQUEST' = 'project/REQUEST';


type Project = {
    name: string,
    info: string,
};


/**
 * Notify that project data is being fetched.
 */
export type RequestAction = {
    +type: typeof REQUEST,
};
export function request(): RequestAction {
    return {
        type: REQUEST,
    };
}


/**
 * Receive project data.
 */
export type ReceiveAction = {
    +type: typeof RECEIVE,
    +name: string,
    +info: string,
};
export function receive(project: Project): ReceiveAction {
    return {
        type: RECEIVE,
        name: project.name,
        info: project.info,
    };
}


/**
 * Get data about the current project.
 */
export function get(slug: string): Function {
    return async dispatch => {
        // When 'all-projects' are selected, we do not fetch data.
        if (slug === 'all-projects') {
            return;
        }
        dispatch(request());
        const results = await api.project.get(slug);
        dispatch(receive(results.data.project));
    }
}


export default {
    get,
    receive,
    request,
};
