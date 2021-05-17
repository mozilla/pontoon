export { default as actions } from './actions';
export { default as reducer } from './reducer';
export { default as selectors } from './selectors';

export { default as PluralSelector } from './components/PluralSelector';

export type { PluralState } from './reducer';

// List of available CLDR plural categories.
export const CLDR_PLURALS: Array<string> = [
    'zero',
    'one',
    'two',
    'few',
    'many',
    'other',
];

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'plural';
