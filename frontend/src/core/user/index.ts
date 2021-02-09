export { default as actions } from './actions';
export { default as reducer } from './reducer';
export { default as selectors } from './selectors';

export { default as SignInLink } from './components/SignInLink';
export { default as UserControls } from './components/UserControls';
export { default as UserAvatar } from './components/UserAvatar';

export type { Settings } from './actions';
export type { SettingsState, UserState, Notification } from './reducer';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'user';
