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
    +bundles: Array<FluentBundle>,
};
export function receive(bundles: Array<FluentBundle>): ReceiveAction {
    return {
        type: RECEIVE,
        bundles,
    };
}


/**
 * Get the UI translations for a list of locales.
 *
 * This fetches the translations for the UI for each given locale, bundles
 * those and store them to be used in showing a localized interface.
 */
export function get(locales: Array<string>): Function {
    return async dispatch => {
        dispatch(request());

        // If 'en-US' is not in the list of locales, add it as the last one.
        // This is because it is recommended to always have a loaded bundle
        // for fluent-react, otherwise some translations will not work as
        // expected, even with their in-code defaults.
        if (!locales.includes('en-US')) {
            locales.push('en-US');
        }

        Promise.all(locales.map(locale => {
            return api.l10n.get(locale)
            .then(content => {
                const bundle = new FluentBundle(locale);
                bundle.addMessages(content);
                return bundle;
            });
        }))
        .then(bundles => {
            dispatch(receive(bundles));
        });
    }
}


export default {
    get,
    receive,
    request,
};
