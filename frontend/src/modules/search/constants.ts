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
