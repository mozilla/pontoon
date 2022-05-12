import { ADD } from './actions';

import type { Action, NotificationMessage } from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const NOTIFICATION = 'notification';

export type NotificationState = {
  readonly message: NotificationMessage | null | undefined;
};

const initial: NotificationState = {
  message: null,
};

export function reducer(
  state: NotificationState = initial,
  action: Action,
): NotificationState {
  return action.type === ADD ? { message: action.message } : state;
}
