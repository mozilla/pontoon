/* @flow */

import { createSelector } from 'reselect';

import * as navigation from 'core/navigation';
import * as plural from 'core/plural';
import * as entitieslist from 'modules/entitieslist';
import * as user from 'core/user';

import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';
import type { Entities } from 'modules/entitieslist';


const entitiesSelector = (state): string => state[entitieslist.NAME].entities;
const userSelector = (state): UserState => state[user.NAME];


export function _getTranslationForSelectedEntity(
    entities: Entities,
    params: NavigationParams,
    pluralForm: number,
): string {
    const entityId = params.entity;
    const entity = entities.find(element => element.pk === entityId);

    if (pluralForm === -1) {
        pluralForm = 0;
    }

    if (
        entity && entity.translation[pluralForm].string &&
        !entity.translation[pluralForm].rejected
    ) {
        return entity.translation[pluralForm].string;
    }

    return '';
}


/**
 * Return the active translation string for the currently selected entity
 * and plural form.
 *
 * The active translation is either the approved one, the fuzzy one, or the
 * most recent non-rejected one.
 */
export const getTranslationForSelectedEntity: Function = createSelector(
    entitiesSelector,
    navigation.selectors.getNavigationParams,
    plural.selectors.getPluralForm,
    _getTranslationForSelectedEntity
);


export function _isReadOnlyEditor(
    entities: Entities,
    params: NavigationParams,
    user: UserState,
): boolean {
    const selectedEntity = entities.find(element => element.pk === params.entity);

    return (
        (selectedEntity && selectedEntity.readonly) ||
        !user.isAuthenticated
    );
}


/**
 * Return true if editor must be read-only, which happens when:
 *   - the entity is read-only OR
 *   - the user is not authenticated
 */
export const isReadOnlyEditor: Function = createSelector(
    entitiesSelector,
    navigation.selectors.getNavigationParams,
    userSelector,
    _isReadOnlyEditor
);


export default {
    getTranslationForSelectedEntity,
    isReadOnlyEditor,
};
