/* @flow */

import { FluentBundle, FluentResource } from '@fluent/bundle';
import { negotiateLanguages } from '@fluent/langneg';

import api from 'core/api';

import { AVAILABLE_LOCALES } from '.';


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

        // Setting defaultLocale to `en-US` means that it will always be the
        // last fallback locale, thus making sure the UI is always working.
        const languages = negotiateLanguages(
            locales,
            AVAILABLE_LOCALES,
            { defaultLocale: 'en-US' },
        );

        const bundles = await Promise.all(languages.map(locale => {
            return api.l10n.get(locale)
            .then(content => {
                const bundle = new FluentBundle(locale);
                const resource = new FluentResource(content);
                bundle.addResource(resource);
                return bundle;
            });
        }));

        dispatch(receive(bundles));
    }
}


export default {
    get,
    receive,
    request,
};
