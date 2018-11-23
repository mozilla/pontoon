/* @flow */

import { createSelector } from 'reselect';


const pathSelector = (state): string => state.router.location.pathname;
const querySelector = (state): string => state.router.location.search;

export type Navigation = {|
    locale: string,
    project: string,
    resource: string,
    entity: number,
    search: ?string,
    status: ?string,
|};

/**
 * Return the locale, project, resource and entity that correspond to the
 * current URL.
 */
export const getNavigation: Function = createSelector(
    pathSelector,
    querySelector,
    (path: string, query: string): Navigation => {
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

        return {
            locale,
            project,
            resource,
            entity,
            search,
            status,
        };
    }
);


export default {
    getNavigation,
};
