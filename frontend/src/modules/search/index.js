/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as SearchBox } from './components/SearchBox';
export { default as withSearch } from './withSearch';


// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'search';


// List of available status filters.
// This list controls the creation of the UI.
export const FILTERS_STATUS = [
    {
        title: 'All',
        slug: 'all',
        stat: 'total',
    },
    {
        title: 'Translated',
        slug: 'translated',
        stat: 'approved',
    },
    {
        title: 'Fuzzy',
        slug: 'fuzzy',
    },
    {
        title: 'Warnings',
        slug: 'warnings',
    },
    {
        title: 'Errors',
        slug: 'errors',
    },
    {
        title: 'Missing',
        slug: 'missing',
    },
    {
        title: 'Unreviewed',
        slug: 'unreviewed',
    },
];


// List of available extra filters.
// This list controls the creation of the UI.
export const FILTERS_EXTRA = [
    {
        title: 'Unchanged',
        slug: 'unchanged',
    },
    {
        title: 'Rejected',
        slug: 'rejected',
    },
];
