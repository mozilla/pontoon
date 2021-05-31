import APIBase from './base';

export default class UXActionAPI extends APIBase {
    /**
     * Log UX action.
     */
    log(
        action_type: string,
        experiment: string | null | undefined,
        data: any | null | undefined,
    ): Promise<any> {
        const csrfToken = this.getCSRFToken();

        const payload = new URLSearchParams();
        payload.append('csrfmiddlewaretoken', csrfToken);
        payload.append('action_type', action_type);

        if (experiment) {
            payload.append('experiment', experiment);
        }

        if (data) {
            payload.append('data', JSON.stringify(data));
        }

        const headers = new Headers();
        headers.append('X-Requested-With', 'XMLHttpRequest');
        headers.append('X-CSRFToken', csrfToken);

        return this.fetch('/log-ux-action/', 'POST', payload, headers);
    }
}
