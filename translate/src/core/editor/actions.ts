import type { Entry } from '@fluent/syntax';

import { SourceType } from '~/api/machinery';
import { FailedChecks } from '~/api/translation';

export const END_UPDATE_TRANSLATION = 'editor/END_UPDATE_TRANSLATION';
export const RESET_EDITOR = 'editor/RESET_EDITOR';
export const RESET_FAILED_CHECKS = 'editor/RESET_FAILED_CHECKS';
export const RESET_HELPER_ELEMENT_INDEX = 'editor/RESET_HELPER_ELEMENT_INDEX';
export const RESET_SELECTION = 'editor/RESET_SELECTION';
export const SELECT_HELPER_ELEMENT_INDEX = 'editor/SELECT_HELPER_ELEMENT_INDEX';
export const SELECT_HELPER_TAB_INDEX = 'editor/SELECT_HELPER_TAB_INDEX';
export const SET_INITIAL_TRANSLATION = 'editor/SET_INITIAL_TRANSLATION';
export const START_UPDATE_TRANSLATION = 'editor/START_UPDATE_TRANSLATION';
export const UPDATE = 'editor/UPDATE';
export const UPDATE_FAILED_CHECKS = 'editor/UPDATE_FAILED_CHECKS';
export const UPDATE_SELECTION = 'editor/UPDATE_SELECTION';
export const UPDATE_MACHINERY_SOURCES = 'editor/UPDATE_MACHINERY_SOURCES';

export type Translation = string | Entry;

export type Action =
  | EndUpdateTranslationAction
  | InitialTranslationAction
  | ResetEditorAction
  | ResetHelperElementIndexAction
  | ResetFailedChecksAction
  | ResetSelectionAction
  | SelectHelperElementIndexAction
  | SelectHelperTabIndexAction
  | StartUpdateTranslationAction
  | UpdateAction
  | UpdateFailedChecksAction
  | UpdateSelectionAction
  | UpdateMachinerySourcesAction;

/**
 * Update the current translation of the selected entity.
 */
export type UpdateAction = {
  readonly type: typeof UPDATE;
  readonly translation: Translation;
  readonly changeSource: string;
};
export function updateTranslation(
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
type UpdateMachinerySourcesAction = {
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
type ResetHelperElementIndexAction = {
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
type SelectHelperElementIndexAction = {
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
type SelectHelperTabIndexAction = {
  readonly type: typeof SELECT_HELPER_TAB_INDEX;
  readonly index: number;
};
export function selectHelperTabIndex(
  index: number,
): SelectHelperTabIndexAction {
  return {
    type: SELECT_HELPER_TAB_INDEX,
    index,
  };
}

/**
 * Update the content that should replace the currently selected text in the
 * active editor.
 */
type InitialTranslationAction = {
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
type UpdateFailedChecksAction = {
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
type ResetSelectionAction = {
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
type ResetEditorAction = {
  readonly type: typeof RESET_EDITOR;
};
export function resetEditor(): ResetEditorAction {
  return {
    type: RESET_EDITOR,
  };
}

/**
 * Reset failed checks to default value.
 */
type ResetFailedChecksAction = {
  readonly type: typeof RESET_FAILED_CHECKS;
};
export function resetFailedChecks(): ResetFailedChecksAction {
  return {
    type: RESET_FAILED_CHECKS,
  };
}

type StartUpdateTranslationAction = {
  readonly type: typeof START_UPDATE_TRANSLATION;
};
export function startUpdateTranslation(): StartUpdateTranslationAction {
  return {
    type: START_UPDATE_TRANSLATION,
  };
}

type EndUpdateTranslationAction = {
  readonly type: typeof END_UPDATE_TRANSLATION;
};
export function endUpdateTranslation(): EndUpdateTranslationAction {
  return {
    type: END_UPDATE_TRANSLATION,
  };
}
