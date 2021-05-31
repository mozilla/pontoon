export { default as actions } from './actions';
export { default as getPluralExamples } from './getPluralExamples';
export { default as reducer } from './reducer';

export type { Locale, Localization } from './actions';
export type { LocaleState } from './reducer';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'locale';
