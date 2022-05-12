export type { ChangeOperation } from '~/api/translation';

export { default as actions } from './actions';
export { History } from './components/History';
export { default as reducer } from './reducer';
export type { HistoryState } from './reducer';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME = 'history';
