import { ADD } from './actions';

import type { AddAction, NotificationMessage } from './actions';

type Action = AddAction;

export type NotificationState = {
  readonly message: NotificationMessage | null | undefined;
};

const initial: NotificationState = {
  message: null,
};

export default function reducer(
  state: NotificationState = initial,
  action: Action,
): NotificationState {
  return action.type === ADD ? { message: action.message } : state;
}
