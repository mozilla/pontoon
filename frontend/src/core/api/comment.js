/* @flow */

import APIBase from './base';


export default class CommentAPI extends APIBase {
    delete(id: number) {
        const payload = new URLSearchParams();
        payload.append('comment', id.toString());

        const headers = new Headers();
        const csrfToken = this.getCSRFToken();
        headers.append('X-Requested-With', 'XMLHttpRequest');
        headers.append('X-CSRFToken', csrfToken);

        return this.fetch('/delete-comment/', 'POST', payload, headers);
    }
}
