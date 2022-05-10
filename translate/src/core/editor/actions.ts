import type { Entry } from '@fluent/syntax';
import NProgress from 'nprogress';

import type { LocaleType } from '~/context/locale';
import type { LocationType } from '~/context/location';
import { PluralFormType } from '~/context/pluralForm';
import type { UnsavedChanges } from '~/context/unsavedChanges';
import api, { Entity, SourceType } from '~/core/api';
import { updateEntityTranslation } from '~/core/entities/actions';
import { addNotification } from '~/core/notification/actions';
import notificationMessages from '~/core/notification/messages';
import { updateResource } from '~/core/resource/actions';
import { updateStats } from '~/core/stats/actions';
import { AppThunk } from '~/store';

export const END_UPDATE_TRANSLATION: 'editor/END_UPDATE_TRANSLATION' =
  'editor/END_UPDATE_TRANSLATION';
export const RESET_EDITOR: 'editor/RESET_EDITOR' = 'editor/RESET_EDITOR';
export const RESET_FAILED_CHECKS: 'editor/RESET_FAILED_CHECKS' =
  'editor/RESET_FAILED_CHECKS';
export const RESET_HELPER_ELEMENT_INDEX: 'editor/RESET_HELPER_ELEMENT_INDEX' =
  'editor/RESET_HELPER_ELEMENT_INDEX';
export const RESET_SELECTION: 'editor/RESET_SELECTION' =
  'editor/RESET_SELECTION';
export const SELECT_HELPER_ELEMENT_INDEX: 'editor/SELECT_HELPER_ELEMENT_INDEX' =
  'editor/SELECT_HELPER_ELEMENT_INDEX';
export const SELECT_HELPER_TAB_INDEX: 'editor/SELECT_HELPER_TAB_INDEX' =
  'editor/SELECT_HELPER_TAB_INDEX';
export const SET_INITIAL_TRANSLATION: 'editor/SET_INITIAL_TRANSLATION' =
  'editor/SET_INITIAL_TRANSLATION';
export const START_UPDATE_TRANSLATION: 'editor/START_UPDATE_TRANSLATION' =
  'editor/START_UPDATE_TRANSLATION';
export const UPDATE: 'editor/UPDATE' = 'editor/UPDATE';
export const UPDATE_FAILED_CHECKS: 'editor/UPDATE_FAILED_CHECKS' =
  'editor/UPDATE_FAILED_CHECKS';
export const UPDATE_SELECTION: 'editor/UPDATE_SELECTION' =
  'editor/UPDATE_SELECTION';
export const UPDATE_MACHINERY_SOURCES: 'editor/UPDATE_MACHINERY_SOURCES' =
  'editor/UPDATE_MACHINERY_SOURCES';

export type Translation = string | Entry;

/**
 * Update the current translation of the selected entity.
 */
export type UpdateAction = {
  readonly type: typeof UPDATE;
  readonly translation: Translation;
  readonly changeSource: string;
};
export function update(
  translation: Translation,
  changeSource?: string,
): UpdateAction {
  return {
    type: UPDATE,
    translation,
    changeSource: changeSource || 'internal',
  };
}

/**
 * Update the content that should replace the currently selected text in the
 * active editor.
 */
export type UpdateSelectionAction = {
  readonly type: typeof UPDATE_SELECTION;
  readonly content: string;
  readonly changeSource: string;
};
export function updateSelection(
  content: string,
  changeSource?: string,
): UpdateSelectionAction {
  return {
    type: UPDATE_SELECTION,
    content,
    changeSource: changeSource || 'internal',
  };
}

/**
 * Update machinerySources and machineryTranslation when copied from machinery tab.
 */
export type UpdateMachinerySourcesAction = {
  readonly type: typeof UPDATE_MACHINERY_SOURCES;
  readonly machinerySources: Array<SourceType>;
  readonly machineryTranslation: string;
};
export function updateMachinerySources(
  machinerySources: Array<SourceType>,
  machineryTranslation: string,
): UpdateMachinerySourcesAction {
  return {
    type: UPDATE_MACHINERY_SOURCES,
    machinerySources,
    machineryTranslation,
  };
}

/**
 * Reset selected helper element index to its initial value.
 */
export type ResetHelperElementIndexAction = {
  readonly type: typeof RESET_HELPER_ELEMENT_INDEX;
};
export function resetHelperElementIndex(): ResetHelperElementIndexAction {
  return {
    type: RESET_HELPER_ELEMENT_INDEX,
  };
}

/**
 * Set selected helper element index to a specific value.
 */
export type SelectHelperElementIndexAction = {
  readonly type: typeof SELECT_HELPER_ELEMENT_INDEX;
  readonly index: number;
};
export function selectHelperElementIndex(
  index: number,
): SelectHelperElementIndexAction {
  return {
    type: SELECT_HELPER_ELEMENT_INDEX,
    index,
  };
}

/**
 * Set selected helper tab index to a specific value.
 */
export type SelectHelperTabIndexAction = {
  readonly type: typeof SELECT_HELPER_TAB_INDEX;
  readonly index: number;
};
function selectHelperTabIndex(index: number): SelectHelperTabIndexAction {
  return {
    type: SELECT_HELPER_TAB_INDEX,
    index,
  };
}

/**
 * Update the content that should replace the currently selected text in the
 * active editor.
 */
export type InitialTranslationAction = {
  readonly type: typeof SET_INITIAL_TRANSLATION;
  readonly translation: Translation;
};
export function setInitialTranslation(
  translation: Translation,
): InitialTranslationAction {
  return {
    type: SET_INITIAL_TRANSLATION,
    translation,
  };
}

/**
 * Update failed checks in the active editor.
 */
export type FailedChecks = {
  readonly clErrors: Array<string>;
  readonly pErrors: Array<string>;
  readonly clWarnings: Array<string>;
  readonly pndbWarnings: Array<string>;
  readonly ttWarnings: Array<string>;
};
export type UpdateFailedChecksAction = {
  readonly type: typeof UPDATE_FAILED_CHECKS;
  readonly failedChecks: FailedChecks;
  readonly source: '' | 'stored' | 'submitted' | number;
};
export function updateFailedChecks(
  failedChecks: FailedChecks,
  source: '' | 'stored' | 'submitted' | number,
): UpdateFailedChecksAction {
  return {
    type: UPDATE_FAILED_CHECKS,
    failedChecks,
    source,
  };
}

/**
 * Reset selected content to default value.
 */
export type ResetSelectionAction = {
  readonly type: typeof RESET_SELECTION;
};
export function resetSelection(): ResetSelectionAction {
  return {
    type: RESET_SELECTION,
  };
}

/**
 * Reset the whole editor's data to its initial value.
 */
export type ResetEditorAction = {
  readonly type: typeof RESET_EDITOR;
};
export function reset(): ResetEditorAction {
  return {
    type: RESET_EDITOR,
  };
}

/**
 * Reset failed checks to default value.
 */
export type ResetFailedChecksAction = {
  readonly type: typeof RESET_FAILED_CHECKS;
};
export function resetFailedChecks(): ResetFailedChecksAction {
  return {
    type: RESET_FAILED_CHECKS,
  };
}
export type StartUpdateTranslationAction = {
  readonly type: typeof START_UPDATE_TRANSLATION;
};

export function startUpdateTranslation(): StartUpdateTranslationAction {
  return {
    type: START_UPDATE_TRANSLATION,
  };
}

export type EndUpdateTranslationAction = {
  readonly type: typeof END_UPDATE_TRANSLATION;
};
export function endUpdateTranslation(): EndUpdateTranslationAction {
  return {
    type: END_UPDATE_TRANSLATION,
  };
}

/**
 * Save the current translation.
 */
export function sendTranslation_(
  entity: Entity,
  translation: string,
  locale: LocaleType,
  { pluralForm, setPluralForm }: PluralFormType,
  forceSuggestions: boolean,
  nextEntity: Entity | null | undefined,
  location: LocationType,
  ignoreWarnings: boolean | null | undefined,
  machinerySources: Array<SourceType>,
  setUnsavedChanges: (next: Partial<UnsavedChanges> | null) => void,
): AppThunk {
  return async (dispatch) => {
    NProgress.start();
    dispatch(startUpdateTranslation());

    const content = await api.translation.create(
      entity.pk,
      translation,
      locale.code,
      pluralForm,
      entity.original,
      forceSuggestions,
      location.resource,
      ignoreWarnings,
      machinerySources,
    );

    if (content.failedChecks) {
      dispatch(updateFailedChecks(content.failedChecks, 'submitted'));
    } else if (content.same) {
      // The translation that was provided is the same as an existing
      // translation for that entity.
      dispatch(addNotification(notificationMessages.SAME_TRANSLATION));
    } else if (content.status) {
      // Notify the user of the change that happened.
      dispatch(addNotification(notificationMessages.TRANSLATION_SAVED));

      // Ignore existing unsavedchanges because they are saved now.
      setUnsavedChanges({ ignore: true });

      dispatch(
        updateEntityTranslation(entity.pk, pluralForm, content.translation),
      );

      // Update stats in the filter panel and resource menu if possible.
      if (content.stats) {
        dispatch(updateStats(content.stats));
        dispatch(
          updateResource(
            entity.path,
            content.stats.approved,
            content.stats.warnings,
          ),
        );
      }

      if (nextEntity) {
        // The change did work, we want to move on to the next Entity or pluralForm.
        if (pluralForm !== -1 && pluralForm < locale.cldrPlurals.length - 1) {
          setPluralForm(pluralForm + 1);
        } else if (nextEntity.pk !== entity.pk) {
          location.push({ entity: nextEntity.pk });
        }
        dispatch(reset());
      }
    }

    dispatch(endUpdateTranslation());
    NProgress.done();
  };
}

export default {
  endUpdateTranslation,
  reset,
  resetFailedChecks,
  resetHelperElementIndex,
  resetSelection,
  selectHelperElementIndex,
  selectHelperTabIndex,
  setInitialTranslation,
  startUpdateTranslation,
  update,
  updateFailedChecks,
  updateSelection,
  updateMachinerySources,
};
