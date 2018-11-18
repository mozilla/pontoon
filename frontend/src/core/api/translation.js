/* @flow */

import APIBase from './base';


export default class TranslationAPI extends APIBase {
    /**
     * Add or update a translation.
     *
     * If a similar translation already exists, update it with the new data.
     * Otherwise, create it.
     */
    updateTranslation(
        entity: number,
        translation: string,
        locale: string,
        pluralForm: number,
        original: string
    ) {
        const csrfToken = this.getCSRFToken();

        const payload = new URLSearchParams();
        payload.append('entity', entity.toString());
        payload.append('translation', translation);
        payload.append('locale', locale);
        payload.append('plural_form', pluralForm.toString());
        payload.append('original', original);
        payload.append('csrfmiddlewaretoken', csrfToken);

        const headers = new Headers();
        headers.append('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
        headers.append('X-Requested-With', 'XMLHttpRequest');
        headers.append('X-CSRFToken', csrfToken);

        return this.fetch('/update/', 'POST', payload, headers);
    }
}
