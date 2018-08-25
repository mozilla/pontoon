/* @flow */

import type { Translation } from './reducer';


export const REQUEST: 'entitieslist/REQUEST' = 'entitieslist/REQUEST';
export const RECEIVE: 'entitieslist/RECEIVE' = 'entitieslist/RECEIVE';
export const UPDATE: 'entitieslist/UPDATE' = 'entitieslist/UPDATE';


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
 * Update the active translation of an entity.
 */
export type UpdateAction = {
    type: typeof UPDATE,
    entity: number,
    translation: Translation,
};
export function updateEntityTranslation(entity: number, translation: Translation): UpdateAction {
    return {
        type: UPDATE,
        entity,
        translation,
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
        const url = new URL('/get-entities/', window.location.origin);
        const payload = new FormData();
        payload.append('locale', locale);
        payload.append('project', project);

        if (resource !== 'all') {
            payload.append('paths[]', resource);
        }

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
    updateEntityTranslation,
};
