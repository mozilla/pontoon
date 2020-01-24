/* @flow */

import APIBase from './base';


export default class CommentAPI extends APIBase {
    add(comment: string, translationId: number) {
        const payload = new URLSearchParams();
        payload.append('comment', comment);
        payload.append('translationId', translationId.toString());

        const headers = new Headers();
        const csrfToken = this.getCSRFToken();
        headers.append('X-Requested-With', 'XMLHttpRequest');
        headers.append('X-CSRFToken', csrfToken);

        return this.fetch('/add-comment/', 'POST', payload, headers);
    }
}
