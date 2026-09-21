import { uploadTranslations } from './upload';

vi.mock('./utils/csrfToken', () => ({
  getCSRFToken: vi.fn(() => 'test-csrf-token'),
}));

function mockFetch(status: number, body: unknown) {
  const fetch = vi.fn(() =>
    Promise.resolve({
      ok: status >= 200 && status < 300,
      status,
      json: () => Promise.resolve(body),
    } as Response),
  );
  vi.stubGlobal('fetch', fetch);
  return fetch;
}

describe('uploadTranslations', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('posts the file and the target of the upload', async () => {
    const fetch = mockFetch(200, { updated: 1 });
    const file = new File(['msgid ""'], 'res.po');

    await uploadTranslations('my', 'proj', 'res.po', file);

    const [url, init] = fetch.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe('/api/v2/upload/translations/');
    expect(init.method).toBe('POST');
    expect(init.headers).toEqual({ 'X-CSRFToken': 'test-csrf-token' });
    const body = init.body as FormData;
    expect(body.get('locale')).toBe('my');
    expect(body.get('project')).toBe('proj');
    expect(body.get('resource')).toBe('res.po');
    expect(body.get('uploadfile')).toBe(file);
  });

  it('returns the result of a successful upload', async () => {
    mockFetch(200, { updated: 1, unchanged: 2, undefined_keys_count: 0 });

    const response = await uploadTranslations(
      'my',
      'proj',
      'res.po',
      new File([], 'f'),
    );

    expect(response.status).toBe(200);
    expect(response.result?.updated).toBe(1);
    expect(response.error).toBeUndefined();
  });

  it('reports the first message of a field error', async () => {
    mockFetch(400, {
      uploadfile: ['Upload failed. File format not supported. Use res.po.'],
    });

    const response = await uploadTranslations(
      'my',
      'proj',
      'res.po',
      new File([], 'f'),
    );

    expect(response.status).toBe(400);
    expect(response.result).toBeUndefined();
    expect(response.error).toBe(
      'Upload failed. File format not supported. Use res.po.',
    );
  });

  it('reports the detail of an error response', async () => {
    mockFetch(409, { detail: 'A concurrent upload changed the same strings.' });

    const response = await uploadTranslations(
      'my',
      'proj',
      'res.po',
      new File([], 'f'),
    );

    expect(response.error).toBe(
      'A concurrent upload changed the same strings.',
    );
  });

  it('reports a network failure without a status', async () => {
    const fetch = vi.fn(() => Promise.reject(new TypeError('Failed to fetch')));
    vi.stubGlobal('fetch', fetch);

    const response = await uploadTranslations(
      'my',
      'proj',
      'res.po',
      new File([], 'f'),
    );

    expect(response).toEqual({ status: 0 });
  });
});
