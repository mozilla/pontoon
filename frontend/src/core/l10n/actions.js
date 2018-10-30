/* @flow */

import { FluentBundle } from 'fluent';

import api from 'core/api';


export const RECEIVE: 'l10n/RECEIVE' = 'l10n/RECEIVE';
export const REQUEST: 'l10n/REQUEST' = 'l10n/REQUEST';


/**
 * Notify that translations for the UI are being fetched.
 */
export type RequestAction = {
    +type: typeof REQUEST,
};
export function request(): RequestAction {
    return {
        type: REQUEST,
    };
}


/**
 * Receive translations for a locale.
 */
export type ReceiveAction = {
    +type: typeof RECEIVE,
    +locale: string,
    +bundle: FluentBundle,
};
export function receive(locale: string, bundle: FluentBundle): ReceiveAction {
    return {
        type: RECEIVE,
        locale,
        bundle,
    };
}


/**
 * Get the UI translations for a locale.
 *
 * This fetches the translations for the UI in a given locale, bundles those
 * and store them to be used in showing a localized interface.
 */
export function get(locale: string): Function {
    return async dispatch => {
        dispatch(request());

        const content = await api.l10n.get(locale);
        const bundle = new FluentBundle(locale);
        bundle.addMessages(content);

        dispatch(receive(locale, bundle))
    }
}


export default {
    get,
    receive,
    request,
};
