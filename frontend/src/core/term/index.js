/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as Term } from './components/Term';
export { default as TermsList } from './components/TermsList';

export type { TermState } from './reducer';


// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'term';
