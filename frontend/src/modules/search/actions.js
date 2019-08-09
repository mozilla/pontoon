/* @flow */

import api from 'core/api';


export const RECEIVE: 'search/RECEIVE' = 'search/RECEIVE';
export const REQUEST: 'search/REQUEST' = 'search/REQUEST';


export type Author = {
    email: string,
    display_name: string,
    id: number,
    gravatar_url: string,
    translation_count: number,
    role: string,
};

export type ResponseType = {
    authors: Array<Author>,
    counts_per_minute: Array<Array<number>>,
};

export type ReceiveAction = {|
    type: typeof RECEIVE,
    response: ResponseType,
|};
export function receive(response: ResponseType): ReceiveAction {
    return {
        type: RECEIVE,
        response,
    };
}


export type RequestAction = {|
    type: typeof REQUEST,
|};
export function request(): RequestAction {
    return {
        type: REQUEST,
    };
}


export function getAuthorsAndTimeRangeData(
    locale: string,
    project: string,
    resource: string,
): Function {
    return async dispatch => {
        dispatch(request());

        const response = await api.filter.get(
            locale,
            project,
            resource,
        );

        dispatch(receive(response));
    };
}


export default {
    getAuthorsAndTimeRangeData,
};
