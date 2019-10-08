/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as AppLocalizationProvider } from './components/AppLocalizationProvider';

export type { L10nState } from './reducer';


// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'l10n';


// List of available locales for the UI.
// Use to choose which locale files to download.
export const AVAILABLE_LOCALES: Array<string> = ['en-US'];


// Enable the use of a special pseudo-localization.
// This turns all localized strings into a weird, accented version, enabling
// to see what is actually localized in the site, and to test strings against
// constraints different from those of English.
// Development feature only.
export const USE_PSEUDO_LOCALIZATION: boolean = true;
