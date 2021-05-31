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
