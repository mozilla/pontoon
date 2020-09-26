/* @flow */

import { createSelector } from 'reselect';

import * as entities from 'core/entities';

import type { EntityTranslation, Entity } from 'core/api';

const pluralSelector = (state): number => state.plural.pluralForm;

export function _getPluralForm(pluralForm: number, entity: ?Entity): number {
    if (pluralForm === -1 && entity && entity.original_plural) {
        return 0;
    }
    return pluralForm;
}

/**
 * Return the plural form to use for the currently selected entity.
 *
 * If the entity has a plural form, and the current plural form is -1,
 * this will correctly return 0 instead of -1. In all other cases, return
 * the plural form as stored in the state.
 */
export const getPluralForm: Function = createSelector(
    pluralSelector,
    entities.selectors.getSelectedEntity,
    _getPluralForm,
);

export function _getTranslationForSelectedEntity(
    entity: Entity,
    pluralForm: number,
): ?EntityTranslation {
    if (pluralForm === -1) {
        pluralForm = 0;
    }

    if (
        entity &&
        entity.translation[pluralForm] &&
        !entity.translation[pluralForm].rejected
    ) {
        return entity.translation[pluralForm];
    }

    return null;
}

/**
 * Return the active translation for the currently selected entity
 * and plural form.
 *
 * The active translation is either the approved one, the fuzzy one, or the
 * most recent non-rejected one.
 */
export const getTranslationForSelectedEntity: Function = createSelector(
    entities.selectors.getSelectedEntity,
    getPluralForm,
    _getTranslationForSelectedEntity,
);

export function _getTranslationStringForSelectedEntity(
    entity: Entity,
    pluralForm: number,
): string {
    const translation = _getTranslationForSelectedEntity(entity, pluralForm);
    if (translation && translation.string) {
        return translation.string;
    }
    return '';
}

/**
 * Return the active translation *string* for the currently selected entity
 * and plural form.
 *
 * The active translation is either the approved one, the fuzzy one, or the
 * most recent non-rejected one.
 */
export const getTranslationStringForSelectedEntity: Function = createSelector(
    entities.selectors.getSelectedEntity,
    getPluralForm,
    _getTranslationStringForSelectedEntity,
);

export default {
    getPluralForm,
    getTranslationForSelectedEntity,
    getTranslationStringForSelectedEntity,
};
