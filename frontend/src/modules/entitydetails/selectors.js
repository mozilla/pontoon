/* @flow */

import { createSelector } from 'reselect';

import * as plural from 'core/plural';
import * as entitieslist from 'modules/entitieslist';
import * as user from 'core/user';

import type { UserState } from 'core/user';
import type { DbEntity } from 'modules/entitieslist';


const userSelector = (state): UserState => state[user.NAME];


export function _getTranslationForSelectedEntity(
    entity: DbEntity,
    pluralForm: number,
): string {
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
    entitieslist.selectors.getSelectedEntity,
    plural.selectors.getPluralForm,
    _getTranslationForSelectedEntity
);


export function _isReadOnlyEditor(
    entity: DbEntity,
    user: UserState,
): boolean {
    return (
        (entity && entity.readonly) ||
        !user.isAuthenticated
    );
}


/**
 * Return true if editor must be read-only, which happens when:
 *   - the entity is read-only OR
 *   - the user is not authenticated
 */
export const isReadOnlyEditor: Function = createSelector(
    entitieslist.selectors.getSelectedEntity,
    userSelector,
    _isReadOnlyEditor
);


export default {
    getTranslationForSelectedEntity,
    isReadOnlyEditor,
};
