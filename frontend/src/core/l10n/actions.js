/* @flow */

import { FluentBundle } from 'fluent/compat';

import api from 'core/api';


export const RECEIVE: 'l10n/RECEIVE' = 'l10n/RECEIVE';
export const REQUEST: 'l10n/REQUEST' = 'l10n/REQUEST';


/**
 * Request translations.
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
 *
 *
 *
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
};
