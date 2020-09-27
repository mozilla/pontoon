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
