/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';
export { default as selectors } from './selectors';

export { default as EntitiesList } from './components/EntitiesList';

export type { DbEntity, Entities } from './reducer';


// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'entities';
