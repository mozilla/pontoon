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

export const SEARCH_OPTIONS = [
  {
    name: 'Search in string identifiers',
    slug: 'search_identifiers',
  },
  {
    name: 'Search in translations only',
    slug: 'search_translations_only',
  },
  {
    name: 'Search in rejected translations',
    slug: 'search_rejected_translations',
  },
  {
    name: 'Match case',
    slug: 'search_match_case',
  },
  {
    name: 'Match whole word',
    slug: 'search_match_whole_word',
  },
] as const;
