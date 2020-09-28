/* @flow */

import api from 'core/api';
import * as stats from 'core/stats';

import type { Entities, EntityTranslation } from 'core/api';

export const RECEIVE: 'entities/RECEIVE' = 'entities/RECEIVE';
export const REQUEST: 'entities/REQUEST' = 'entities/REQUEST';
export const RESET: 'entities/RESET' = 'entities/RESET';
export const UPDATE: 'entities/UPDATE' = 'entities/UPDATE';

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
    entities: Entities,
    hasMore: boolean,
};
export function receive(entities: Entities, hasMore: boolean): ReceiveAction {
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
    pluralForm: number,
    translation: EntityTranslation,
};
export function updateEntityTranslation(
    entity: number,
    pluralForm: number,
    translation: EntityTranslation,
): UpdateAction {
    return {
        type: UPDATE,
        entity,
        pluralForm,
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
    entityIds: ?Array<number>,
    exclude: Array<number>,
    entity: ?string,
    search: ?string,
    status: ?string,
    extra: ?string,
    tag: ?string,
    author: ?string,
    time: ?string,
): Function {
    return async (dispatch) => {
        dispatch(request());

        const content = await api.entity.getEntities(
            locale,
            project,
            resource,
            entityIds,
            exclude,
            entity,
            search,
            status,
            extra,
            tag,
            author,
            time,
        );

        if (content.entities) {
            dispatch(receive(content.entities, content.has_next));
            dispatch(stats.actions.update(content.stats));
        }
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
