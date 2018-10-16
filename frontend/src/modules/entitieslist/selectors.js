/* @flow */

import { createSelector } from 'reselect';

import * as navigation from 'core/navigation';
import type { Navigation } from 'core/navigation';

import { NAME } from '.';
import type { Entities, DbEntity } from './reducer';


const entitiesSelector = (state): string => state[NAME].entities;


export function _getSelectedEntity(
    entities: Entities,
    params: Navigation,
): ?DbEntity {
    return entities.find(element => element.pk === params.entity);
}


/**
 * Return the currently selected Entity object.
 */
export const getSelectedEntity: Function = createSelector(
    entitiesSelector,
    navigation.selectors.getNavigation,
    _getSelectedEntity
);


export default {
    getSelectedEntity,
};
