/* @flow */

import api from 'core/api';


export const RECEIVE: 'locales/RECEIVE' = 'locales/RECEIVE';
export const REQUEST: 'locales/REQUEST' = 'locales/REQUEST';

export type Locale = {|
    +code: string,
    +name: string,
    +cldrPlurals: Array<number>,
    +pluralRule: string,
    +direction: string,
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
    locale: Locale,
|};
export function receive(locale: Locale) {
    return {
        type: RECEIVE,
        locale,
    };
}


export function get(code: string): Function {
    return async dispatch => {
        dispatch(request());

        const results = await api.locale.get(code);
        const data = results.data.locale;
        const locale = {
            ...data,
            direction: data.direction.toLowerCase(),
            cldrPlurals: data.cldrPlurals.split(',').map(i => parseInt(i, 10)),
        }

        dispatch(receive(locale));
    }
}

export default {
    request,
    get,
};
