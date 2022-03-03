import APIBase from './base';

export default class UXActionAPI extends APIBase {
  /**
   * Log UX action.
   */
  async log(
    action_type: string,
    experiment: string | null | undefined,
    data: any | null | undefined,
  ): Promise<void> {
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

    try {
      await this.fetch('/log-ux-action/', 'POST', payload, headers);
    } catch (_) {
      /* Ignore errors during UX action logging */
    }
  }
}
