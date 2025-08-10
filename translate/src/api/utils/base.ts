type FetchOptions = {
  headers?: Headers;
  signal?: AbortSignal;
  /** If `true`, any previous request for the same URL is aborted. */
  singleton?: boolean;
};

export function GET(
  url: string,
  search?: URLSearchParams | null,
  options: FetchOptions = {},
): Promise<any> {
  const fullUrl = new URL(url, window.location.origin);
  if (search) {
    fullUrl.search = String(search);
  }
  return wrapFetch(String(fullUrl), options, {
    method: 'GET',
    credentials: 'same-origin',
  });
}

export function POST(
  url: string,
  body: FormData | URLSearchParams,
  options: FetchOptions = {},
): Promise<any> {
  const fullUrl = new URL(url, window.location.origin);
  return wrapFetch(String(fullUrl), options, {
    method: 'POST',
    credentials: 'same-origin',
    body,
  });
}

const aborts = new Map<string, AbortController>();

async function wrapFetch(
  url: string,
  { headers = new Headers(), signal, singleton }: FetchOptions,
  init: RequestInit,
): Promise<any> {
  headers.append('X-Requested-With', 'XMLHttpRequest');
  init.headers = headers;

  if (signal) {
    init.signal = signal;
  } else if (singleton) {
    const prev = aborts.get(url);
    if (prev) {
      prev.abort();
    }
    const ac = new AbortController();
    aborts.set(url, ac);
    init.signal = ac.signal;
  }

  let response: Response | undefined;
  try {
    response = await fetch(url, init);
    return await response.json();
  } catch (error: unknown) {
    if (error instanceof Error) {
      switch (error.name) {
        case 'AbortError':
          // Swallow Abort errors because we trigger them ourselves.
          return {};

        case 'SyntaxError':
          /* eslint-disable no-console */
          if (response?.ok) {
            console.error('The response content is not JSON-compatible');
            console.error(`URL: ${url} - Method: ${init.method}`);
            console.error(error);
          } else if (response?.status !== 404) {
            console.error(
              `Unexpected HTTP response ${response?.status} ${response?.statusText} for ${init.method} ${url}`,
            );
          }
          return {};
      }
    }
    throw error;
  }
}
