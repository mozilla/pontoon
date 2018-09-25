/* @flow */


export default class APIBase {
    getCSRFToken(): string {
        let csrfToken = '';
        const rootElt = document.getElementById('root');
        if (rootElt) {
            csrfToken = rootElt.dataset.csrfToken;
        }
        return csrfToken;
    }

    getFullURL(url: string): URL {
        return new URL(url, window.location.origin);
    }

    async fetch(
        url: string,
        method: string,
        payload: URLSearchParams | FormData | null,
        headers: Headers,
    ): Promise<Object> {
        const fullUrl = this.getFullURL(url);

        const requestParams = {};
        requestParams.method = method;
        requestParams.credentials = 'same-origin';
        requestParams.headers = headers;

        if (payload !== null) {
            if (method === 'POST') {
                requestParams.body = payload;
            }
            else if (method === 'GET') {
                fullUrl.search = payload.toString();
            }
        }

        const response = await fetch(
            fullUrl,
            requestParams
        );

        return await response.json();
    }
}
