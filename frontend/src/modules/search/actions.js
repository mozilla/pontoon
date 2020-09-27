/* @flow */

import api from 'core/api';

export const UPDATE: 'search/UPDATE' = 'search/UPDATE';
export const SET_FOCUS: 'search/SET_FOCUS' = 'search/SET_FOCUS';

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

export type UpdateAction = {|
    type: typeof UPDATE,
    response: ResponseType,
|};
export function update(response: ResponseType): UpdateAction {
    return {
        type: UPDATE,
        response,
    };
}

export function getAuthorsAndTimeRangeData(
    locale: string,
    project: string,
    resource: string,
): Function {
    return async (dispatch) => {
        const response = await api.filter.get(locale, project, resource);

        dispatch(update(response));
    };
}

export type SetFocusAction = {|
    type: typeof SET_FOCUS,
    searchInputFocused: boolean,
|};
export function setFocus(searchInputFocused: boolean): SetFocusAction {
    return {
        type: SET_FOCUS,
        searchInputFocused,
    };
}

export default {
    getAuthorsAndTimeRangeData,
    setFocus,
};
