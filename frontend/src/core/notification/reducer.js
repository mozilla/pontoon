/* @flow */

import { Localized } from 'fluent-react';

import { ADD } from './actions';

import type { AddAction, NotificationType } from './actions';


type Action =
    | AddAction
;


type NotificationMessage = {|
    +type: NotificationType,
    +content: string | typeof Localized,
|};


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
