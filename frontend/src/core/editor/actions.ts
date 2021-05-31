import NProgress from 'nprogress';

import api from 'core/api';

import { actions as entitiesActions } from 'core/entities';
import * as notification from 'core/notification';
import { actions as pluralActions } from 'core/plural';
import { actions as resourceActions } from 'core/resource';
import { actions as statsActions } from 'core/stats';
import * as unsavedchanges from 'modules/unsavedchanges';

import type { Entity, SourceType } from 'core/api';
import type { Locale } from 'core/locale';
import type { Entry } from '@fluent/syntax';

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
function selectHelperElementIndex(
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

function startUpdateTranslation(): StartUpdateTranslationAction {
    return {
        type: START_UPDATE_TRANSLATION,
    };
}

export type EndUpdateTranslationAction = {
    readonly type: typeof END_UPDATE_TRANSLATION;
};
function endUpdateTranslation(): EndUpdateTranslationAction {
    return {
        type: END_UPDATE_TRANSLATION,
    };
}

/**
 * Save the current translation.
 */
export function sendTranslation(
    entity: Entity,
    translation: string,
    locale: Locale,
    pluralForm: number,
    forceSuggestions: boolean,
    nextEntity: Entity | null | undefined,
    router: Record<string, any>,
    resource: string,
    ignoreWarnings: boolean | null | undefined,
    machinerySources: Array<SourceType>,
): (...args: Array<any>) => any {
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
            resource,
            ignoreWarnings,
            machinerySources,
        );

        if (content.failedChecks) {
            dispatch(updateFailedChecks(content.failedChecks, 'submitted'));
        } else if (content.same) {
            // The translation that was provided is the same as an existing
            // translation for that entity.
            dispatch(
                notification.actions.add(
                    notification.messages.SAME_TRANSLATION,
                ),
            );
        } else if (content.status) {
            // Notify the user of the change that happened.
            dispatch(
                notification.actions.add(
                    notification.messages.TRANSLATION_SAVED,
                ),
            );

            // Ignore existing unsavedchanges because they are saved now.
            dispatch(unsavedchanges.actions.ignore());

            dispatch(
                entitiesActions.updateEntityTranslation(
                    entity.pk,
                    pluralForm,
                    content.translation,
                ),
            );

            // Update stats in the filter panel and resource menu if possible.
            if (content.stats) {
                dispatch(statsActions.update(content.stats));
                dispatch(
                    resourceActions.update(
                        entity.path,
                        content.stats.approved,
                        content.stats.warnings,
                    ),
                );
            }

            if (nextEntity) {
                // The change did work, we want to move on to the next Entity or pluralForm.
                pluralActions.moveToNextTranslation(
                    dispatch,
                    router,
                    entity.pk,
                    nextEntity.pk,
                    pluralForm,
                    locale,
                );
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
    sendTranslation,
    selectHelperElementIndex,
    selectHelperTabIndex,
    setInitialTranslation,
    startUpdateTranslation,
    update,
    updateFailedChecks,
    updateSelection,
    updateMachinerySources,
};
