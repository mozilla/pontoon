/* @flow */

import api from 'core/api';

export const RECEIVE: 'locale/RECEIVE' = 'locale/RECEIVE';
export const REQUEST: 'locale/REQUEST' = 'locale/REQUEST';

export type Localization = {|
    +totalStrings: number,
    +approvedStrings: number,
    +stringsWithWarnings: number,
    +project: {|
        +slug: string,
        +name: string,
    |},
|};

export type Locale = {|
    +code: string,
    +name: string,
    +cldrPlurals: Array<number>,
    +pluralRule: string,
    +direction: string,
    +script: string,
    +googleTranslateCode: string,
    +msTranslatorCode: string,
    +systranTranslateCode: string,
    +msTerminologyCode: string,
    +transvision: boolean,
    +localizations: Array<Localization>,
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
    return async (dispatch) => {
        dispatch(request());

        const results = await api.locale.get(code);
        const data = results.data.locale;
        const locale = {
            ...data,
            direction: data.direction.toLowerCase(),
            cldrPlurals: data.cldrPlurals
                .split(',')
                .map((i) => parseInt(i, 10)),
        };

        dispatch(receive(locale));
    };
}

export default {
    receive,
    request,
    get,
};
