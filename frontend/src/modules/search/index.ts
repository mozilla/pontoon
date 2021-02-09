export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as SearchBox } from './components/SearchBox';
export { default as withSearch } from './withSearch';

export { Author } from './actions';
export { SearchAndFilters } from './reducer';
export { TimeRangeType } from './components/SearchBox';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'search';
