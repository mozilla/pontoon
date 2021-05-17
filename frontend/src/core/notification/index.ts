export { default as actions } from './actions';
export { default as reducer } from './reducer';
export { default as messages } from './messages';

export { default as NotificationPanel } from './components/NotificationPanel';

export type { NotificationState } from './reducer';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'notification';
