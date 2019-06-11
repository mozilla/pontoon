/* @flow */

import { createSelector } from 'reselect';

import * as entitieslist from 'modules/entitieslist';

import type { DbEntity } from 'modules/entitieslist';


const pluralSelector = (state): number => state.plural.pluralForm;


export function _getPluralForm(pluralForm: number, entity: ?DbEntity): number {
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
    entitieslist.selectors.getSelectedEntity,
    _getPluralForm
);


export default {
    getPluralForm,
};
