export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as Machinery } from './components/Machinery';
export { default as MachineryCount } from './components/Count';

export type { MachineryState } from './reducer';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'machinery';
