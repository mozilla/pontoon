import { fetchGPTTransform } from './machinery';
import * as base from './utils/base';

vi.mock('./utils/base', () => ({
  GET: vi.fn(),
  POST: vi.fn(() => Promise.resolve({ translation: 'resultado' })),
}));

vi.mock('./utils/csrfToken', () => ({
  getCSRFToken: vi.fn(() => 'test-csrf-token'),
}));

describe('fetchGPTTransform', () => {
  const POST = vi.mocked(base.POST);

  it('sends required params', async () => {
    await fetchGPTTransform('hello', 'hola', 'informal', 'es');

    const [url, params] = POST.mock.calls[0] as [string, URLSearchParams];
    expect(url).toBe('/gpt-transform/');
    expect(params.get('english_text')).toBe('hello');
    expect(params.get('translated_text')).toBe('hola');
    expect(params.get('characteristic')).toBe('informal');
    expect(params.get('locale')).toBe('es');
  });

  it('omits entity_pk when not provided', async () => {
    await fetchGPTTransform('hello', 'hola', 'informal', 'es');

    const [, params] = POST.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('entity_pk')).toBeNull();
  });

  it('includes entity_pk when provided', async () => {
    await fetchGPTTransform('hello', 'hola', 'informal', 'es', 42);

    const [, params] = POST.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('entity_pk')).toBe('42');
  });

  it('returns the translation from the response', async () => {
    const result = await fetchGPTTransform('hello', 'hola', 'informal', 'es');

    expect(result).toEqual([
      {
        sources: ['gpt-transform'],
        original: 'hello',
        translation: 'resultado',
      },
    ]);
  });

  it('returns empty array when response has no translation', async () => {
    POST.mockResolvedValueOnce({});
    const result = await fetchGPTTransform('hello', 'hola', 'informal', 'es');
    expect(result).toEqual([]);
  });
});
