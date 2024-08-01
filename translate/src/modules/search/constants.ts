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
    name: 'Pretranslated',
    slug: 'pretranslated',
    stat: 'pretranslated',
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
] as const;

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
    name: 'Fuzzy',
    slug: 'fuzzy',
  },
  {
    name: 'Rejected',
    slug: 'rejected',
  },
  {
    name: 'Missing without Unreviewed',
    slug: 'missing-without-unreviewed',
  },
] as const;

export const FILTERS_SEARCH = [
  {
    name: 'Search context identifiers',
    slug: 'identifiers',
  },
  // {
  //   name: 'Search translations only',
  //   slug: 'translations',
  // },
  // {
  //   name: 'Search rejected translations',
  //   slug: 'rejected',
  // },
  // {
  //   name: 'Match whole words',
  //   slug: 'matchWords',
  // },
  // {
  //   name: 'Match case',
  //   slug: 'matchCase',
  // },
] as const;
