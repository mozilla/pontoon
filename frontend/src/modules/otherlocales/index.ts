export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as OtherLocales } from './components/OtherLocales';
export { default as OtherLocalesCount } from './components/Count';

export type { LocalesState } from './reducer';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'otherlocales';
