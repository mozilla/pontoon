import APIBase from './base';
import type { SourceType } from './types';

export default class TranslationAPI extends APIBase {
    /**
     * Create a new translation.
     *
     * If a similar translation already exists, update it with the new data.
     * Otherwise, create it.
     */
    create(
        entity: number,
        translation: string,
        locale: string,
        pluralForm: number,
        original: string,
        forceSuggestions: boolean,
        resource: string,
        ignoreWarnings: boolean | null | undefined,
        machinerySources: Array<SourceType>,
    ): Promise<any> {
        const csrfToken = this.getCSRFToken();

        const payload = new URLSearchParams();
        payload.append('entity', entity.toString());
        payload.append('translation', translation);
        payload.append('locale', locale);
        payload.append('plural_form', pluralForm.toString());
        payload.append('original', original);
        payload.append('force_suggestions', forceSuggestions.toString());
        payload.append('machinery_sources', machinerySources.toString());

        if (resource !== 'all-resources') {
            payload.append('paths[]', resource);
        }

        if (ignoreWarnings) {
            payload.append('ignore_warnings', ignoreWarnings.toString());
        }

        payload.append('csrfmiddlewaretoken', csrfToken);

        const headers = new Headers();
        headers.append(
            'Content-Type',
            'application/x-www-form-urlencoded; charset=UTF-8',
        );
        headers.append('X-Requested-With', 'XMLHttpRequest');
        headers.append('X-CSRFToken', csrfToken);

        return this.fetch('/translations/create/', 'POST', payload, headers);
    }

    _changeStatus(
        url: string,
        id: number,
        resource: string,
        ignoreWarnings: boolean | null | undefined,
    ): Promise<any> {
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

    approve(
        id: number,
        resource: string,
        ignoreWarnings: boolean | null | undefined,
    ): Promise<any> {
        return this._changeStatus(
            '/translations/approve/',
            id,
            resource,
            ignoreWarnings,
        );
    }

    unapprove(id: number, resource: string): Promise<any> {
        return this._changeStatus(
            '/translations/unapprove/',
            id,
            resource,
            false,
        );
    }

    reject(id: number, resource: string): Promise<any> {
        return this._changeStatus('/translations/reject/', id, resource, false);
    }

    unreject(id: number, resource: string): Promise<any> {
        return this._changeStatus(
            '/translations/unreject/',
            id,
            resource,
            false,
        );
    }

    delete(id: number): Promise<any> {
        const payload = new URLSearchParams();
        payload.append('translation', id.toString());

        const headers = new Headers();
        const csrfToken = this.getCSRFToken();
        headers.append('X-Requested-With', 'XMLHttpRequest');
        headers.append('X-CSRFToken', csrfToken);

        return this.fetch('/translations/delete/', 'POST', payload, headers);
    }
}
