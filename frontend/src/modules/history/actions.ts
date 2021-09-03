import NProgress from 'nprogress';

import api from 'core/api';

import { actions as editorActions } from 'core/editor';
import { actions as entitiesActions } from 'core/entities';
import * as notification from 'core/notification';
import { actions as pluralActions } from 'core/plural';
import { actions as resourceActions } from 'core/resource';
import { actions as statsActions } from 'core/stats';

import type { Entity, TranslationComment } from 'core/api';
import type { Locale } from 'core/locale';

export const RECEIVE: 'history/RECEIVE' = 'history/RECEIVE';
export const REQUEST: 'history/REQUEST' = 'history/REQUEST';
export const UPDATE: 'history/UPDATE' = 'history/UPDATE';

export type HistoryTranslation = {
    readonly approved: boolean;
    readonly approvedUser: string;
    readonly date: string;
    readonly dateIso: string;
    readonly fuzzy: boolean;
    readonly pk: number;
    readonly rejected: boolean;
    readonly string: string;
    readonly uid: number | null | undefined;
    readonly unapprovedUser: string;
    readonly machinerySources: string;
    readonly user: string;
    readonly username: string;
    readonly userGravatarUrlSmall: string;
    readonly comments: Array<TranslationComment>;
};

export type ReceiveAction = {
    readonly type: typeof RECEIVE;
    readonly translations: Array<HistoryTranslation>;
};
export function receive(
    translations: Array<HistoryTranslation>,
): ReceiveAction {
    return {
        type: RECEIVE,
        translations,
    };
}

export type UpdateAction = {
    readonly type: typeof UPDATE;
    readonly translation: HistoryTranslation;
};
export function update(translation: HistoryTranslation): UpdateAction {
    return {
        type: UPDATE,
        translation,
    };
}

export type RequestAction = {
    readonly type: typeof REQUEST;
    readonly entity: number;
    readonly pluralForm: number;
};
export function request(entity: number, pluralForm: number): RequestAction {
    return {
        type: REQUEST,
        entity,
        pluralForm,
    };
}

export function get(
    entity: number,
    locale: string,
    pluralForm: number,
): (...args: Array<any>) => any {
    return async (dispatch) => {
        // request() must be called separately to prevent
        // re-rendering of the component on addComment()

        // Abort all previously running requests.
        await api.entity.abort();

        const content = await api.entity.getHistory(entity, locale, pluralForm);

        dispatch(receive(content));
    };
}

export type ChangeOperation = 'approve' | 'unapprove' | 'reject' | 'unreject';

function updateStatusOnServer(
    change: ChangeOperation,
    translation: number,
    resource: string,
    ignoreWarnings: boolean | null | undefined,
): Promise<Record<string, any>> {
    switch (change) {
        case 'approve':
            return api.translation.approve(
                translation,
                resource,
                ignoreWarnings,
            );
        case 'unapprove':
            return api.translation.unapprove(translation, resource);
        case 'reject':
            return api.translation.reject(translation, resource);
        case 'unreject':
            return api.translation.unreject(translation, resource);
        default:
            throw new Error('Unexpected translation status change: ' + change);
    }
}

function _getOperationNotif(change: ChangeOperation, success: boolean) {
    if (success) {
        switch (change) {
            case 'approve':
                return notification.messages.TRANSLATION_APPROVED;
            case 'unapprove':
                return notification.messages.TRANSLATION_UNAPPROVED;
            case 'reject':
                return notification.messages.TRANSLATION_REJECTED;
            case 'unreject':
                return notification.messages.TRANSLATION_UNREJECTED;
            default:
                throw new Error(
                    'Unexpected translation status change: ' + change,
                );
        }
    } else {
        switch (change) {
            case 'approve':
                return notification.messages.UNABLE_TO_APPROVE_TRANSLATION;
            case 'unapprove':
                return notification.messages.UNABLE_TO_UNAPPROVE_TRANSLATION;
            case 'reject':
                return notification.messages.UNABLE_TO_REJECT_TRANSLATION;
            case 'unreject':
                return notification.messages.UNABLE_TO_UNREJECT_TRANSLATION;
            default:
                throw new Error(
                    'Unexpected translation status change: ' + change,
                );
        }
    }
}

export function updateStatus(
    change: ChangeOperation,
    entity: Entity,
    locale: Locale,
    resource: string,
    pluralForm: number,
    translation: number,
    nextEntity: Entity | null | undefined,
    router: Record<string, any>,
    ignoreWarnings?: boolean | null | undefined,
): (...args: Array<any>) => any {
    return async (dispatch) => {
        NProgress.start();

        const results = await updateStatusOnServer(
            change,
            translation,
            resource,
            ignoreWarnings,
        );

        // Update the UI based on the response.
        if (results.failedChecks) {
            dispatch(editorActions.update(results.string, 'external'));
            dispatch(
                editorActions.updateFailedChecks(
                    results.failedChecks,
                    translation,
                ),
            );
        } else {
            // Show a notification to explain what happened.
            const notif = _getOperationNotif(change, !!results.translation);
            dispatch(notification.actions.add(notif));

            if (results.translation && change === 'approve' && nextEntity) {
                // The change did work, we want to move on to the next Entity or pluralForm.
                pluralActions.moveToNextTranslation(
                    dispatch,
                    router,
                    entity.pk,
                    nextEntity.pk,
                    pluralForm,
                    locale,
                );
                dispatch(editorActions.reset());
            } else {
                dispatch(get(entity.pk, locale.code, pluralForm));
            }
        }

        if (results.stats) {
            // Update stats in the progress chart and the filter panel.
            dispatch(statsActions.update(results.stats));

            // Update stats in the resource menu.
            dispatch(
                resourceActions.update(
                    entity.path,
                    results.stats.approved,
                    results.stats.warnings,
                ),
            );
        }

        // Update entity translation data now that it has changed on the server.
        if (results.translation) {
            dispatch(
                entitiesActions.updateEntityTranslation(
                    entity.pk,
                    pluralForm,
                    results.translation,
                ),
            );
        }

        NProgress.done();
    };
}

export function deleteTranslation(
    entity: number,
    locale: string,
    pluralForm: number,
    translation: number,
): (...args: Array<any>) => any {
    return async (dispatch) => {
        NProgress.start();

        const results = await api.translation.delete(translation);

        if (results.status) {
            dispatch(
                notification.actions.add(
                    notification.messages.TRANSLATION_DELETED,
                ),
            );
            dispatch(get(entity, locale, pluralForm));
        } else {
            dispatch(
                notification.actions.add(
                    notification.messages.UNABLE_TO_DELETE_TRANSLATION,
                ),
            );
        }

        NProgress.done();
    };
}

export default {
    get,
    receive,
    request,
    updateStatus,
    deleteTranslation,
};
