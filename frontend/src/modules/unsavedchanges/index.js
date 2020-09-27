/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as UnsavedChanges } from './components/UnsavedChanges';

export type { UnsavedChangesState } from './reducer';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'unsavedchanges';
