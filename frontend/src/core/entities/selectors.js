/* @flow */

import { createSelector } from 'reselect';

import * as navigation from 'core/navigation';

import { NAME } from '.';

import type { Entities, Entity } from 'core/api/types';
import type { NavigationParams } from 'core/navigation';


const entitiesSelector = (state): string => state[NAME].entities;


export function _getSelectedEntity(
    entities: Entities,
    params: NavigationParams,
): ?Entity {
    return entities.find(element => element.pk === params.entity);
}


/**
 * Return the currently selected Entity object.
 */
export const getSelectedEntity: Function = createSelector(
    entitiesSelector,
    navigation.selectors.getNavigationParams,
    _getSelectedEntity
);


export function _getNextEntity(
    entities: Entities,
    params: NavigationParams,
): ?Entity {
    const currentIndex = entities.findIndex(element => element.pk === params.entity);

    if (currentIndex === -1) {
        return null;
    }

    const next = (currentIndex + 1 >= entities.length) ? 0 : currentIndex + 1;
    return entities[next];
}


/**
 * Return the Entity that follows the current one in the list.
 */
export const getNextEntity: Function = createSelector(
    entitiesSelector,
    navigation.selectors.getNavigationParams,
    _getNextEntity
);


export function _getPreviousEntity(
    entities: Entities,
    params: NavigationParams,
): ?Entity {
    const currentIndex = entities.findIndex(element => element.pk === params.entity);

    if (currentIndex === -1) {
        return null;
    }

    const previous = (currentIndex === 0) ? entities.length - 1 : currentIndex - 1;
    return entities[previous];
}


/**
 * Return the Entity that preceeds the current one in the list.
 */
export const getPreviousEntity: Function = createSelector(
    entitiesSelector,
    navigation.selectors.getNavigationParams,
    _getPreviousEntity
);


export default {
    getNextEntity,
    getPreviousEntity,
    getSelectedEntity,
};
