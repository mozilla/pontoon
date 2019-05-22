/* @flow */

export { default as SearchBox } from './components/SearchBox';


// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'search';


// List of available status filters.
// This list controls the creation of the UI.
export const FILTERS_STATUS = [
    { title: 'All', tag: 'all', stat: 'total' },
    { title: 'Translated', tag: 'translated', stat: 'approved' },
    { title: 'Fuzzy', tag: 'fuzzy' },
    { title: 'Warnings', tag: 'warnings' },
    { title: 'Errors', tag: 'errors' },
    { title: 'Missing', tag: 'missing' },
    { title: 'Unreviewed', tag: 'unreviewed' },
];
