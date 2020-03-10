/* @flow */

import APIBase from './base';


export default class CommentAPI extends APIBase {
    add(
        entity: number,
        locale: string,
        comment: string,
        translation: ?number,
    ) {
        const payload = new URLSearchParams();
        payload.append('entity', entity.toString());
        payload.append('locale', locale);
        payload.append('comment', comment);
        if (translation) {
            payload.append('translation', translation.toString());
        }

        const headers = new Headers();
        const csrfToken = this.getCSRFToken();
        headers.append('X-Requested-With', 'XMLHttpRequest');
        headers.append('X-CSRFToken', csrfToken);

        return this.fetch('/add-comment/', 'POST', payload, headers);
    }

    /**
     * Get all users usernames and emails from server.
     */
    async getUsers(): Promise<Object> {
        const headers = new Headers();
        headers.append('X-Requested_With', 'XMLHttpRequest');

        return await this.fetch('/get-users/', 'GET', null, headers);
    }
}
