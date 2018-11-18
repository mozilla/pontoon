/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';
export { default as selectors } from './selectors';

export { default as PluralSelector } from './components/PluralSelector';

export type { PluralState } from './reducer';


// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'plural';
