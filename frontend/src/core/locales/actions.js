/* @flow */

import api from 'core/api';

export const RECEIVE: 'locales/RECEIVE' = 'locales/RECEIVE';
export const REQUEST: 'locales/REQUEST' = 'locales/REQUEST';

export type Locale = {|
    +code: string,
    +cldrPlurals: Array<number>,
    +pluralRule: string,
    +direction: string,
    +name: string,
|};


export type RequestAction = {|
    type: typeof REQUEST,
|};
export function request() {
    return {
        type: REQUEST,
    };
}


export type ReceiveAction = {|
    type: typeof RECEIVE,
    locales: { [string]: Locale },
|};
export function receive(locales: { [string]: Locale }) {
    return {
        type: RECEIVE,
        locales,
    };
}


export function get(): Function {
    return async dispatch => {
        dispatch(request());

        const results = await api.locale.getAll();
        const locales = {};
        results.data.locales.forEach(locale => {
            locales[locale.code] = {
                ...locale,
                cldrPlurals: locale.cldrPlurals.split(',').map(i => parseInt(i, 10)),
            };
        });

        dispatch(receive(locales));
    }
}

export default {
    request,
    get,
};
