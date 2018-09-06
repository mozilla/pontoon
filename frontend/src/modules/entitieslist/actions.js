/* @flow */

import api from 'core/api';

import type { Translation } from './reducer';


export const RECEIVE: 'entitieslist/RECEIVE' = 'entitieslist/RECEIVE';
export const REQUEST: 'entitieslist/REQUEST' = 'entitieslist/REQUEST';
export const RESET: 'entitieslist/RESET' = 'entitieslist/RESET';
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
    hasMore: boolean,
};
export function receive(entities: Array<Object>, hasMore: boolean): ReceiveAction {
    return {
        type: RECEIVE,
        entities,
        hasMore,
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
export function updateEntityTranslation(
   entity: number,
   translation: Translation
): UpdateAction {
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
    exclude: ?Array<number>,
): Function {
    return async dispatch => {
        dispatch(request());

        const content = await api.entity.getEntities(
            locale,
            project,
            resource,
            exclude,
        );
        dispatch(receive(content.entities, content.has_next));
    };
}


export type ResetAction = {
   type: typeof RESET,
};
export function reset(): ResetAction {
    return {
        type: RESET,
    };
}


export default {
    get,
    receive,
    request,
    reset,
    updateEntityTranslation,
};
