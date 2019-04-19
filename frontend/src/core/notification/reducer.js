/* @flow */

import { ADD } from './actions';

import type { AddAction, NotificationType } from './actions';


type Action =
    | AddAction
;


export type NotificationMessage = {|
    +type: NotificationType,
    +message: string,
    +status: 'new' | 'read',
|};


// Read-only state (marked by '+').
export type NotificationState = {|
    +messages: Array<NotificationMessage>,
|};


const initial: NotificationState = {
    messages: [],
};

export default function reducer(
    state: NotificationState = initial,
    action: Action,
): NotificationState {
    switch (action.type) {
        case ADD:
            return {
                messages: [
                    {
                        type: action.contentType,
                        message: action.message,
                        status: 'new',
                    },
                ],
            };
        default:
            return state;
    }
}
