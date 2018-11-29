/* @flow */

import api from 'core/api';
import { actions as listActions } from 'modules/entitieslist';


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
    resource: string
): Promise<Object> {
    switch (change) {
        case 'approve':
            return api.translation.approve(translation, resource);
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
): Function {
    return async dispatch => {
        const results = await updateStatusOnServer(change, translation, resource);
        dispatch(get(entity, locale, pluralForm));
        dispatch(listActions.updateEntityTranslation(entity, pluralForm, results.translation));
    }
}


export default {
    get,
    receive,
    request,
    reset,
    updateStatus,
};
