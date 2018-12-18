/* @flow */

import { createSelector } from 'reselect';

import * as navigation from 'core/navigation';
import type { NavigationParams } from 'core/navigation';

import { NAME } from '.';
import type { Entities, DbEntity } from './reducer';


const entitiesSelector = (state): string => state[NAME].entities;


export function _getSelectedEntity(
    entities: Entities,
    params: NavigationParams,
): ?DbEntity {
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
    params: Navigation,
): ?DbEntity {
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
    navigation.selectors.getNavigation,
    _getNextEntity
);


export default {
    getNextEntity,
    getSelectedEntity,
};
