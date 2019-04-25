/* @flow */

import { Localized } from 'fluent-react';


export const ADD: 'notification/ADD' = 'notification/ADD';


export type NotificationType = 'error' | 'info';

export type NotificationMessage = {|
    content: typeof Localized,
    type: NotificationType,
|};


/**
 * Add a notification to display.
 */
export type AddAction = {
    type: typeof ADD,
    message: NotificationMessage,
};
export function add(message: NotificationMessage): AddAction {
    return {
        type: ADD,
        message,
    };
}


export default {
    add,
};
