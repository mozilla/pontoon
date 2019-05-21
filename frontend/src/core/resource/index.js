/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as ResourceItem } from './components/ResourceItem';
export { default as ResourceMenu } from './components/ResourceMenu';
export { default as ResourcePercent } from './components/ResourcePercent';

export type { Resource } from './actions';
export type { ResourcesState } from './reducer';


// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'resource';
