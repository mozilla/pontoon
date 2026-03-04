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

// `default` is the default value for each search option. A value matching
// the default will be omitted from the URL, a value differing from it is
// passed explicitly.
export const SEARCH_OPTIONS = [
  {
    name: 'Match case',
    slug: 'search_match_case',
    default: false,
  },
  {
    name: 'Match whole word',
    slug: 'search_match_whole_word',
    default: false,
  },
  {
    name: 'Include string identifiers',
    slug: 'search_identifiers',
    default: false,
  },
  {
    name: 'Include rejected translations',
    slug: 'search_rejected_translations',
    default: false,
  },
  {
    name: 'Exclude source strings',
    slug: 'search_exclude_source_strings',
    default: false,
  },
] as const;

export const SEARCH_OPTION_KEYS = SEARCH_OPTIONS.map(
  ({ slug }) => slug,
) as Array<(typeof SEARCH_OPTIONS)[number]['slug']>;

export const DEFAULT_SEARCH_OPTIONS = Object.fromEntries(
  SEARCH_OPTIONS.map(({ slug, default: def }) => [slug, def]),
) as Record<(typeof SEARCH_OPTIONS)[number]['slug'], boolean>;
