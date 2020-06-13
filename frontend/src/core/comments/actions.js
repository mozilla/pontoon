/* @flow */

import NProgress from 'nprogress';

import api from 'core/api';
import * as notification from 'core/notification';
import * as history from 'modules/history';
import * as teamcomments from 'modules/teamcomments';

import type { UsersList } from 'core/api';

export const RECEIVE: 'users/RECEIVE' = 'users/RECEIVE';


export type ReceiveAction = {|
    +type: typeof RECEIVE,
    +users: Array<UsersList>,    
|}

export function receive(
    users: Array<UsersList>,
): ReceiveAction {
    return {
        type: RECEIVE,
        users,
    };
}

export function addComment(
    entity: number,
    locale: string,
    pluralForm: number,
    translation: ?number,
    comment: string,
): Function {
    return async dispatch => {
        NProgress.start();

        await api.comment.add(entity, locale, comment, translation);

        dispatch(notification.actions.add(notification.messages.COMMENT_ADDED));
        if (translation) {
            dispatch(history.actions.get(entity, locale, pluralForm));
        }
        else {
            dispatch(teamcomments.actions.get(entity, locale));
        }

        NProgress.done();
    }
}

export function get(): Function {
    return async dispatch => {
        const content = await api.comment.getUsers();
        dispatch(receive(content));
    }
}


export default {
    addComment,
    get,
};
