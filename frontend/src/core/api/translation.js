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
        original: string,
        forceSuggestions: boolean,
        resource: string,
        ignoreWarnings: ?boolean,
    ) {
        const csrfToken = this.getCSRFToken();

        const payload = new URLSearchParams();
        payload.append('entity', entity.toString());
        payload.append('translation', translation);
        payload.append('locale', locale);
        payload.append('plural_form', pluralForm.toString());
        payload.append('original', original);
        payload.append('force_suggestions', forceSuggestions.toString());

        if (resource !== 'all-resources') {
            payload.append('paths[]', resource);
        }

        if (ignoreWarnings) {
            payload.append('ignore_warnings', ignoreWarnings.toString());
        }

        payload.append('csrfmiddlewaretoken', csrfToken);

        const headers = new Headers();
        headers.append('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
        headers.append('X-Requested-With', 'XMLHttpRequest');
        headers.append('X-CSRFToken', csrfToken);

        return this.fetch('/update/', 'POST', payload, headers);
    }

    _changeStatus(url: string, id: number, resource: string, ignoreWarnings: ?boolean) {
        const csrfToken = this.getCSRFToken();

        const payload = new URLSearchParams();
        payload.append('translation', id.toString());

        if (resource !== 'all-resources') {
            payload.append('paths[]', resource);
        }

        if (ignoreWarnings) {
            payload.append('ignore_warnings', ignoreWarnings.toString());
        }

        const headers = new Headers();
        headers.append('X-Requested-With', 'XMLHttpRequest');
        headers.append('X-CSRFToken', csrfToken);

        return this.fetch(url, 'POST', payload, headers);
    }

    approve(id: number, resource: string, ignoreWarnings: ?boolean) {
        return this._changeStatus('/approve-translation/', id, resource, ignoreWarnings);
    }

    unapprove(id: number, resource: string) {
        return this._changeStatus('/unapprove-translation/', id, resource);
    }

    reject(id: number, resource: string) {
        return this._changeStatus('/reject-translation/', id, resource);
    }

    unreject(id: number, resource: string) {
        return this._changeStatus('/unreject-translation/', id, resource);
    }

    delete(id: number) {
        const payload = new URLSearchParams();
        payload.append('translation', id.toString());

        const headers = new Headers();
        const csrfToken = this.getCSRFToken();
        headers.append('X-Requested-With', 'XMLHttpRequest');
        headers.append('X-CSRFToken', csrfToken);

        return this.fetch('/delete-translation/', 'POST', payload, headers);
    }
}
