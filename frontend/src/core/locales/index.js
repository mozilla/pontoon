/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';
export { default as selectors } from './selectors';

export type { Locale } from './actions';
export type { LocalesState } from './reducer';


// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'locales';
