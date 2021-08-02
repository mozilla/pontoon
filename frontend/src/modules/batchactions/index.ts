export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as BatchActions } from './components/BatchActions';

export type { BatchActionsState } from './reducer';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME = 'batchactions';
