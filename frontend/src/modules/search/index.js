/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as SearchBox } from './components/SearchBox';
export { default as withSearch } from './withSearch';

export type { Author } from './actions';
export type { SearchAndFilters } from './reducer';
export type { TimeRangeType } from './components/SearchBox';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'search';

// List of available status filters.
// This list controls the creation of the UI.
export const FILTERS_STATUS = [
    {
        name: 'All',
        slug: 'all',
        stat: 'total',
    },
    {
        name: 'Translated',
        slug: 'translated',
        stat: 'approved',
    },
    {
        name: 'Fuzzy',
        slug: 'fuzzy',
    },
    {
        name: 'Warnings',
        slug: 'warnings',
    },
    {
        name: 'Errors',
        slug: 'errors',
    },
    {
        name: 'Missing',
        slug: 'missing',
    },
    {
        name: 'Unreviewed',
        slug: 'unreviewed',
    },
];

// List of available extra filters.
// This list controls the creation of the UI.
export const FILTERS_EXTRA = [
    {
        name: 'Unchanged',
        slug: 'unchanged',
    },
    {
        name: 'Empty',
        slug: 'empty',
    },
    {
        name: 'Rejected',
        slug: 'rejected',
    },
];
