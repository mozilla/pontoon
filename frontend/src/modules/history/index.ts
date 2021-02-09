export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as History } from './components/History';

export type { ChangeOperation } from './actions';
export type { HistoryTranslation, HistoryState } from './reducer';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'history';
