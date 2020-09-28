/* @flow */

import { ADD } from './actions';

import type { AddAction, NotificationMessage } from './actions';

type Action = AddAction;

export type NotificationState = {|
    +message: ?NotificationMessage,
|};

const initial: NotificationState = {
    message: null,
};

export default function reducer(
    state: NotificationState = initial,
    action: Action,
): NotificationState {
    switch (action.type) {
        case ADD:
            return {
                message: action.message,
            };
        default:
            return state;
    }
}
