/* @flow */

import { createSelector } from 'reselect';

import { selectors as navSelectors } from 'core/navigation';
import type { Navigation } from 'core/navigation';

import { NAME } from '.';
import type { Entities, DbEntity } from './reducer';


const entitiesSelector = (state): string => state[NAME].entities;


export function _getTranslationForSelectedEntity(
    entities: Entities,
    params: Navigation,
): string {
    const entityId = params.entity;
    const entity = entities.find(element => element.pk === entityId);
    if (entity && entity.translation[0].string && !entity.translation[0].rejected) {
        return entity.translation[0].string;
    }
    return '';
}


/**
 * Return the active translation string for the currently selected Entity.
 *
 * The active translation is either the approved one, the fuzzy one, or the
 * most recent non-rejected one.
 */
export const getTranslationForSelectedEntity: Function = createSelector(
    entitiesSelector,
    navSelectors.getNavigation,
    _getTranslationForSelectedEntity
);


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
    navSelectors.getNavigation,
    _getSelectedEntity
);


export default {
    getTranslationForSelectedEntity,
    getSelectedEntity,
};
