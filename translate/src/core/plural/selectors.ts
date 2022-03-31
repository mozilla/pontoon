import { createSelector } from 'reselect';

import * as entities from '~/core/entities';

import type { EntityTranslation, Entity } from '~/core/api';
import type { RootState } from '../../store';

const pluralSelector = (state: RootState) => state.plural.pluralForm;

export function _getPluralForm(
  pluralForm: number,
  entity: Entity | null | undefined,
): number {
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
export const getPluralForm = createSelector(
  pluralSelector,
  (state: RootState) => entities.selectors.getSelectedEntity(state),
  _getPluralForm,
);

export function _getTranslationForSelectedEntity(
  entity: Entity | undefined,
  pluralForm: number,
): EntityTranslation | null | undefined {
  if (pluralForm === -1) pluralForm = 0;
  const pf = entity?.translation[pluralForm];
  return pf && !pf.rejected ? pf : null;
}

/**
 * Return the active translation for the currently selected entity
 * and plural form.
 *
 * The active translation is either the approved one, the pretranslated one, the fuzzy one, or the
 * most recent non-rejected one.
 */
export const getTranslationForSelectedEntity = createSelector(
  (state: RootState) => entities.selectors.getSelectedEntity(state),
  getPluralForm,
  _getTranslationForSelectedEntity,
);

export function _getTranslationStringForSelectedEntity(
  entity: Entity | undefined,
  pluralForm: number,
): string {
  const translation = _getTranslationForSelectedEntity(entity, pluralForm);
  return translation?.string ?? '';
}

/**
 * Return the active translation *string* for the currently selected entity
 * and plural form.
 *
 * The active translation is either the approved one, the pretranslated one, the fuzzy one, or the
 * most recent non-rejected one.
 */
export const getTranslationStringForSelectedEntity = createSelector(
  (state: RootState) => entities.selectors.getSelectedEntity(state),
  getPluralForm,
  _getTranslationStringForSelectedEntity,
);

export default {
  getPluralForm,
  getTranslationForSelectedEntity,
  getTranslationStringForSelectedEntity,
};
