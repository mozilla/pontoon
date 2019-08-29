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
    +script: string,
    +googleTranslateCode: string,
    +msTranslatorCode: string,
    +msTerminologyCode: string,
    +transvision: boolean,
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


export function get(code: string): Function {
    return async dispatch => {
        dispatch(request());

        const results = await api.locale.get(code);
        const locale = results.data.locale;

        const locales = {
            [locale.code]: {
                ...locale,
                direction: locale.direction.toLowerCase(),
                cldrPlurals: locale.cldrPlurals.split(',').map(i => parseInt(i, 10)),
            }
        };

        dispatch(receive(locales));
    }
}

export default {
    request,
    get,
};
