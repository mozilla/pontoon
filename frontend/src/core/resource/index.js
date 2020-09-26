/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as ResourceMenu } from './components/ResourceMenu';

export type { Resource } from './actions';
export type { ResourcesState } from './reducer';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'resource';
