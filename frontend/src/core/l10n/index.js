/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as AppLocalizationProvider } from './components/AppLocalizationProvider';

export type { L10nState } from './reducer';


// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'l10n';
