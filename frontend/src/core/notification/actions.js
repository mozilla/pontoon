/* @flow */

export const ADD: 'notification/ADD' = 'notification/ADD';


export type NotificationType = 'error' | 'info';


/**
 * Add a notification to display.
 */
export type AddAction = {
    type: typeof ADD,
    message: string,
    contentType: NotificationType,
};
export function add(message: string, type: NotificationType): AddAction {
    return {
        type: ADD,
        message,
        contentType: type,
    };
}


export default {
    add,
};
