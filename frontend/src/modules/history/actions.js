/* @flow */

import api from 'core/api';
import { actions as listActions } from 'modules/entitieslist';


export const RECEIVE: 'history/RECEIVE' = 'history/RECEIVE';
export const REQUEST: 'history/REQUEST' = 'history/REQUEST';
export const UPDATE: 'history/UPDATE' = 'history/UPDATE';


export type ReceiveAction = {|
    +type: typeof RECEIVE,
    +entity: number,
    +translations: Array<Object>,
|};
export function receive(entity: number, translations: Array<Object>): ReceiveAction {
    return {
        type: RECEIVE,
        entity,
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
    +entity: number,
|};
export function request(entity: number): RequestAction {
    return {
        type: REQUEST,
        entity,
    };
}


export function get(entity: number, locale: string, pluralForm: number): Function {
    return async dispatch => {
        dispatch(request(entity));
        const content = await api.entity.getHistory(entity, locale, pluralForm);
        dispatch(receive(entity, content));
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


function updateStatusInState(change: string, translation: number): Function {
    return dispatch => {
        let newTranslation;

        switch (change) {
            case 'approve':
                newTranslation = {
                    pk: translation,
                    approved: true,
                    fuzzy: false,
                    rejected: false,
                };
                break;
            case 'reject':
                newTranslation = {
                    pk: translation,
                    approved: false,
                    fuzzy: false,
                    rejected: true,
                };
                break;
            case 'unapprove':
            case 'unreject':
                newTranslation = {
                    pk: translation,
                    approved: false,
                    fuzzy: false,
                    rejected: false,
                };
                break;
            default:
                throw new Error('Unexpected translation status change: ' + change);
        }

        dispatch(update(newTranslation));
    }
}


export function updateStatus(
    change: string,
    entity: number,
    pluralForm: number,
    translation: number,
    resource: string
): Function {
    return async dispatch => {
        const results = await updateStatusOnServer(change, translation, resource);
        dispatch(updateStatusInState(change, translation));
        dispatch(listActions.updateEntityTranslation(entity, pluralForm, results.translation));
    }
}


export default {
    get,
    receive,
    request,
    updateStatus,
};
