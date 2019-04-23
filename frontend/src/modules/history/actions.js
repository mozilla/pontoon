/* @flow */

import api from 'core/api';

import { actions as navActions } from 'core/navigation';
import * as notification from 'core/notification';
import { actions as statsActions } from 'core/stats';
import { actions as editorActions } from 'modules/editor';
import { actions as listActions } from 'modules/entitieslist';

import type { DbEntity } from 'modules/entitieslist';


export const RECEIVE: 'history/RECEIVE' = 'history/RECEIVE';
export const REQUEST: 'history/REQUEST' = 'history/REQUEST';
export const RESET: 'history/RESET' = 'history/RESET';
export const UPDATE: 'history/UPDATE' = 'history/UPDATE';


export type ReceiveAction = {|
    +type: typeof RECEIVE,
    +translations: Array<Object>,
|};
export function receive(translations: Array<Object>): ReceiveAction {
    return {
        type: RECEIVE,
        translations,
    };
}


export type UpdateAction = {|
    +type: typeof UPDATE,
    +translation: Object,
|};
export function update(translation: Object) {
    return {
        type: UPDATE,
        translation,
    };
}


export type RequestAction = {|
    +type: typeof REQUEST,
|};
export function request(): RequestAction {
    return {
        type: REQUEST,
    };
}


export type ResetAction = {|
    +type: typeof RESET,
|};
export function reset(): ResetAction {
    return {
        type: RESET,
    };
}


export function get(entity: number, locale: string, pluralForm: number): Function {
    return async dispatch => {
        dispatch(request());
        const content = await api.entity.getHistory(entity, locale, pluralForm);
        dispatch(receive(content));
    }
}


function updateStatusOnServer(
    change: string,
    translation: number,
    resource: string,
    ignoreWarnings: ?boolean,
): Promise<Object> {
    switch (change) {
        case 'approve':
            return api.translation.approve(translation, resource, ignoreWarnings);
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


export function updateStatus(
    change: string,
    entity: number,
    locale: string,
    resource: string,
    pluralForm: number,
    translation: number,
    nextEntity: ?DbEntity,
    router: Object,
    ignoreWarnings: ?boolean,
): Function {
    return async dispatch => {
        const results = await updateStatusOnServer(
            change, translation, resource, ignoreWarnings
        );

        // Show a notification to explain what happened.
        if (results.translation) {
            let statusChange = change;
            if (change.endsWith('e')) {
                statusChange += 'd';
            }
            else {
                statusChange += 'ed';
            }
            dispatch(
                notification.actions.add('Translation ' + statusChange, 'info')
            );
        }
        else {
            dispatch(
                notification.actions.add(`Unable to ${change} translation`, 'error')
            );
        }

        // Update the UI based on the response.
        if (results.failedChecks) {
            dispatch(editorActions.update(results.string, 'external'));
            dispatch(editorActions.updateFailedChecks(results.failedChecks, translation));
        }
        else if (
            results.translation &&
            change === 'approve' &&
            nextEntity &&
            nextEntity.pk !== entity
        ) {
            // The change did work, we want to move on to the next Entity.
            dispatch(navActions.updateEntity(router, nextEntity.pk.toString()));
        }
        else {
            dispatch(get(entity, locale, pluralForm));
        }

        // Update stats for the search panel if possible.
        if (results.stats) {
            dispatch(statsActions.update(results.stats));
        }

        // Refresh the data now that it has changed on the server.
        if (results.translation) {
            dispatch(
                listActions.updateEntityTranslation(entity, pluralForm, results.translation)
            );
        }
    }
}


export function deleteTranslation(
    entity: number,
    locale: string,
    pluralForm: number,
    translation: number,
): Function {
    return async dispatch => {
        await api.translation.delete(translation);
        dispatch(
            notification.actions.add('Translation deleted', 'info')
        );
        dispatch(get(entity, locale, pluralForm));
    }
}


export default {
    get,
    receive,
    request,
    reset,
    updateStatus,
    deleteTranslation,
};
