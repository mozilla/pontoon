import { strip } from './strip';
import { getCSRFToken } from './csrf';

export class DjangoAjax {
    /**
     * This is a wrapper for window.fetch, adding the Headers and form vars
     * required for Django's xhr/csrf protection
     *
     * It only injects headers if it deems the target URL to be "same-origin"
     * to prevent leaking of csrf data
     */

    get csrf() {
        /**
         * This is the canonical Django way to retrieve csrf:
         *    return cookies.get('csrftoken');
         * which is not implemented 8/
         */
        throw new Error('Django csrf not implemented');
    }

    get headers() {
        /**
         * default Headers are set with Django's xhr/csrf
         * and have `accept` set to "application/json"
         */
        return new Headers({
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': this.csrf,
            Accept: 'application/json',
        });
    }

    appendParams(container, data) {
        /**
         * For a given data container - either FormData/URLSearchParams
         * appends data from an object
         *
         * If any of the object values are arrayish, it will append k=v[n]
         * for each item n of v
         */
        Object.entries(data || {}).forEach(([k, v]) => {
            if (Array.isArray(v)) {
                v.forEach((item) => container.append(k, item));
            } else {
                container.append(k, v);
            }
        });
        return container;
    }

    asGetParams(data) {
        /**
         * Mangle a data object to URLSearchParams
         */
        return this.appendParams(new URLSearchParams(), data);
    }

    asMultipartForm(data) {
        /**
         * Mangle a data object to FormData
         */
        return this.appendParams(new FormData(), data);
    }

    fetch(url, data, params) {
        /**
         * This is a convenience method to allow the API
         * to be programatically called.
         *
         * Defaults to `get`, and currently only implements `get`
         * and `post`
         */
        let { method } = params || {};
        method = method || 'get';
        if (['get', 'GET'].indexOf(method) !== -1) {
            return this.get(url, data, params);
        } else if (['post', 'POST'].indexOf(method) !== -1) {
            return this.post(url, data, params);
        } else {
            throw new Error('Unrecognized fetch command: ' + method);
        }
    }

    get(url, data, options) {
        /**
         * Calls window.fetch with method=get, and request params
         * as provided by getRequest
         *
         */
        options = options || {};
        options.method = 'GET';
        options.params = this.asGetParams(data);
        return window.fetch(url, this.getRequest(url, options));
    }

    getCredentials(url) {
        /**
         * Gets the "credentials" - ie "same-origin", "cors" etc
         *
         * Matches window URL with requested URL to determine
         * credentials.
         *
         */
        if (this.isSameOrigin(url)) {
            return 'same-origin';
        }
    }

    getRequest(url, options) {
        /**
         * Builds a request object as expected by window.fetch
         *
         */
        return Object.assign(
            { credentials: this.getCredentials(url), headers: this.headers },
            options,
        );
    }

    isSameOrigin(url) {
        /**
         * Matches the protocol, domain and port
         *
         * If URLs are relative to the domain they will be
         * regared as same-origin
         *
         */
        let { origin, domain, port } = this._parsedLocation;
        const parsedURL = this._parseURL(url, port);
        return (
            parsedURL === domain ||
            parsedURL === origin ||
            !/^(\/\/|http:|https:).*/.test(parsedURL)
        );
    }

    post(url, data, options) {
        /**
         * Calls window.fetch with method=post, and request params
         * as provided by getRequest
         *
         */
        options = options || {};
        options.method = 'POST';
        if (this.isSameOrigin(url)) {
            data.csrfmiddlewaretoken = this.csrf;
        }
        options.body = this.asMultipartForm(data);
        return window.fetch(url, this.getRequest(url, options));
    }

    _parseURL(url, port) {
        const parser = document.createElement('a');
        parser.href = url;
        let parsedURL = parser.protocol + '//' + parser.hostname;
        if (parser.port !== '') {
            parsedURL = parsedURL + ':' + parser.port;
        } else if (!/^(\/\/|http:|https:).*/.test(url) && port) {
            parsedURL = parsedURL + ':' + port;
        }
        return parsedURL;
    }

    get _parsedLocation() {
        let hostname = strip.rstrip(window.location.hostname, '/');
        const protocol = window.location.protocol;
        const port = window.location.port;
        if (port) {
            hostname += ':' + port;
        }
        const origin = '//' + hostname;
        const domain = protocol + origin;
        return { origin, domain, port };
    }
}

export class PontoonDjangoAjax extends DjangoAjax {
    get csrf() {
        // this is a bit sketchy but the only afaict way due to session_csrf
        return getCSRFToken();
    }
}

export const ajax = new PontoonDjangoAjax();
