/* @flow */

import isEmpty from 'lodash.isempty';

import api from 'core/api';

import type { TermType } from 'core/api';

export const RECEIVE: 'terms/RECEIVE' = 'terms/RECEIVE';
export const REQUEST: 'terms/REQUEST' = 'terms/REQUEST';

export type ReceiveAction = {|
    +type: typeof RECEIVE,
    +terms: Array<TermType>,
|};
export function receive(terms: Array<TermType>): ReceiveAction {
    return {
        type: RECEIVE,
        terms,
    };
}

export type RequestAction = {|
    +type: typeof REQUEST,
    +sourceString: string,
|};
export function request(sourceString: string): RequestAction {
    return {
        type: REQUEST,
        sourceString,
    };
}

export function get(sourceString: string, locale: string): Function {
    return async (dispatch) => {
        dispatch(request(sourceString));

        // Abort all previously running requests.
        await api.entity.abort();

        let content = await api.entity.getTerms(sourceString, locale);

        // The default return value of aborted requests is {},
        // which is incompatible with reducer
        if (isEmpty(content)) {
            content = [];
        }

        dispatch(receive(content));
    };
}

export default {
    get,
    receive,
    request,
};
