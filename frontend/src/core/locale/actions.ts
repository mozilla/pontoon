import api from 'core/api';

export const RECEIVE: 'locale/RECEIVE' = 'locale/RECEIVE';
export const REQUEST: 'locale/REQUEST' = 'locale/REQUEST';

export type Localization = {
    readonly totalStrings: number;
    readonly approvedStrings: number;
    readonly stringsWithWarnings: number;
    readonly project: {
        readonly slug: string;
        readonly name: string;
    };
};

export type Locale = {
    readonly code: string;
    readonly name: string;
    readonly cldrPlurals: Array<number>;
    readonly pluralRule: string;
    readonly direction: string;
    readonly script: string;
    readonly googleTranslateCode: string;
    readonly msTranslatorCode: string;
    readonly systranTranslateCode: string;
    readonly msTerminologyCode: string;
    readonly localizations: Array<Localization>;
};

export type RequestAction = {
    type: typeof REQUEST;
};
export function request(): RequestAction {
    return {
        type: REQUEST,
    };
}

export type ReceiveAction = {
    type: typeof RECEIVE;
    locale: Locale;
};
export function receive(locale: Locale): ReceiveAction {
    return {
        type: RECEIVE,
        locale,
    };
}

export function get(code: string): (...args: Array<any>) => any {
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
