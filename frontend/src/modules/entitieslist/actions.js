/* @flow */

export const REQUEST: 'entitieslist/REQUEST' = 'entitieslist/REQUEST';
export const RECEIVE: 'entitieslist/RECEIVE' = 'entitieslist/RECEIVE';


/**
 * Indicate that entities are currently being fetched.
 */
export type RequestAction = {
    type: typeof REQUEST,
};
export function request(): RequestAction {
    return {
        type: REQUEST,
    };
}


/**
 * Update entities to a new set.
 */
export type ReceiveAction = {
    type: typeof RECEIVE,
    entities: Array<Object>,
};
export function receive(entities: Array<Object>): ReceiveAction {
    return {
        type: RECEIVE,
        entities,
    };
}


/**
 * Fetch entities and their translation.
 */
export function get(
    locale: string,
    project: string,
    resource: string,
): Function {
    return async (dispatch: Function): Promise<void> => {
        dispatch(request());

        // Fetch entities from backend.
        const url = new URL('http://localhost:8000/get-entities/');
        const payload = new FormData();
        payload.append('locale', locale);
        payload.append('project', project);
        payload.append('paths[]', resource);

        const requestParams = {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: payload,
        };

        const response = await fetch(url, requestParams);
        const content = await response.json();
        dispatch(receive(content.entities));
    };
}

export default {
    get,
    receive,
    request,
};
