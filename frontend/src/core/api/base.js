/* @flow */

import 'abortcontroller-polyfill/dist/abortcontroller-polyfill-only';


export default class APIBase {
    abortController: AbortController;
    signal: ?AbortSignal;

    constructor() {
        // Create a controller to abort fetch requests.
        this.abortController = new AbortController();
        this.signal = this.abortController.signal;
    }

    abort() {
        // Abort the previously started requests.
        this.abortController.abort();

        // Now create a new controller for the next round of requests.
        this.abortController = new AbortController();
        this.signal = this.abortController.signal;
    }

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

        // This signal is used to cancel requests with the `abort()` method.
        requestParams.signal = this.signal;

        if (payload !== null) {
            if (method === 'POST') {
                requestParams.body = payload;
            }
            else if (method === 'GET') {
                fullUrl.search = payload.toString();
            }
        }

        let response;
        try {
            response = await fetch(
                fullUrl,
                requestParams
            );
        }
        catch (e) {
            // Swallow Abort errors because we trigger them ourselves.
            if (e.name === 'AbortError') {
                return {};
            }
            throw e;
        }

        try {
            return await response.json();
        }
        catch (e) {
            // Catch non-JSON responses
            console.error('The response content is not JSON-compatible');
            console.error(`URL: ${url} - Method: ${method}`);
            console.error(e);

            return {};
        }
    }
}
