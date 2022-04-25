function asFormData(data) {
  /**
   * Mangle a data object to FormData
   *
   * If any of the object values are arrayish, it will append k=v[n]
   * for each item n of v
   */
  const formData = new FormData();
  if (data) {
    for (const [k, v] of Object.entries(data)) {
      if (Array.isArray(v)) {
        for (const item of v) {
          formData.append(k, item);
        }
      } else {
        formData.append(k, v);
      }
    }
  }
  return formData;
}

function getLocation() {
  let hostname = window.location.hostname;
  const protocol = window.location.protocol;
  const port = window.location.port;
  if (port) {
    hostname += ':' + port;
  }
  const origin = '//' + hostname;
  const domain = protocol + origin;
  return { origin, domain, port };
}

function parseURL(url, port) {
  const parser = document.createElement('a');
  parser.href = url;
  let parsedURL = parser.protocol + '//' + parser.hostname;
  if (parser.port !== '') {
    parsedURL += ':' + parser.port;
  } else if (!/^(\/\/|http:|https:).*/.test(url) && port) {
    parsedURL += ':' + port;
  }
  return parsedURL;
}

/**
 * Matches the protocol, domain and port
 *
 * If URLs are relative to the domain they will be
 * regared as same-origin
 */
export function isSameOrigin(url) {
  const { origin, domain, port } = getLocation();
  const parsedURL = parseURL(url, port);
  return (
    parsedURL === domain ||
    parsedURL === origin ||
    !/^(\/\/|http:|https:).*/.test(parsedURL)
  );
}

/**
 * This is a wrapper for window.fetch, adding the Headers and form vars
 * required for Django's xhr/csrf protection
 *
 * It only injects headers if it deems the target URL to be "same-origin"
 * to prevent leaking of csrf data
 */
export function post(url, data) {
  // this is a bit sketchy but the only afaict way due to session_csrf
  const csrf = document.querySelector('input[name=csrfmiddlewaretoken]').value;

  const init = {
    body: asFormData(data),
    headers: new Headers({
      Accept: 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
      'X-CSRFToken': csrf,
    }),
    method: 'POST',
  };
  if (isSameOrigin(url)) {
    init.body.append('csrfmiddlewaretoken', csrf);
    init.credentials = 'same-origin';
  }

  return window.fetch(url, init);
}
