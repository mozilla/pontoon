/* @flow */

import { ADD } from './actions';

import type { AddAction, NotificationType } from './actions';


type Action =
    | AddAction
;


export type NotificationMessage = {|
    +type: NotificationType,
    +message: string,
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
                message: {
                    type: action.contentType,
                    message: action.message,
                },
            };
        default:
            return state;
    }
}
