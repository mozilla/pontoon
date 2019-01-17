/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as UserAutoUpdater } from './components/UserAutoUpdater';

export type { Settings } from './actions';
export type { UserState } from './reducer';


// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'user';
