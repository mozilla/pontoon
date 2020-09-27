/* @flow */

import { createSelector } from 'reselect';

const pathSelector = (state): string => state.router.location.pathname;
const querySelector = (state): string => state.router.location.search;

export type NavigationParams = {|
    locale: string,
    project: string,
    resource: string,
    entity: number,
    search: ?string,
    status: ?string,
    extra: ?string,
    tag: ?string,
    author: ?string,
    time: ?string,
|};

/**
 * Return the locale, project, resource and entity that correspond to the
 * current URL.
 */
export const getNavigationParams: Function = createSelector(
    pathSelector,
    querySelector,
    (path: string, query: string): NavigationParams => {
        const parts = path.split('/');

        // Because pathname always starts and finishes with a '/',
        // the first and last elements of `parts` are empty strings.
        parts.shift();
        parts.pop();

        const locale = parts.shift();
        const project = parts.shift();
        const resource = parts.join('/');

        const params = new URLSearchParams(query);
        const entity = Number(params.get('string'));
        const search = params.get('search');
        const status = params.get('status');
        const extra = params.get('extra');
        const tag = params.get('tag');
        const author = params.get('author');
        const time = params.get('time');

        return {
            locale,
            project,
            resource,
            entity,
            search,
            status,
            extra,
            tag,
            author,
            time,
        };
    },
);

export default {
    getNavigationParams,
};
