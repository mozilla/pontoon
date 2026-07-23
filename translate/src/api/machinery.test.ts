import type { Locale } from '~/context/Locale';

import { fetchComposedMachinery, fetchGPTTransform } from './machinery';
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

describe('fetchComposedMachinery', () => {
  const GET = vi.mocked(base.GET);
  const locale = { code: 'fr' } as Locale;

  it('sends entity, locale, and service params', async () => {
    GET.mockResolvedValueOnce({
      value: ['composed'],
      properties: {},
      sources: ['translation-memory'],
    });

    await fetchComposedMachinery(42, locale, 'translation-memory');

    const [url, params] = GET.mock.calls[0] as [string, URLSearchParams];
    expect(url).toBe('/machinery-composed/');
    expect(params.get('entity')).toBe('42');
    expect(params.get('locale')).toBe('fr');
    expect(params.get('service')).toBe('translation-memory');
  });

  it('returns a ComposedMachineryTranslation with the response data model', async () => {
    GET.mockResolvedValueOnce({
      value: ['Click Me'],
      properties: { title: ['Tip'] },
      sources: ['translation-memory', 'google-translate'],
    });

    const result = await fetchComposedMachinery(1, locale, 'google-translate');

    expect(result).toEqual([
      {
        sources: ['translation-memory', 'google-translate'],
        value: ['Click Me'],
        properties: { title: ['Tip'] },
        quality: undefined,
      },
    ]);
  });

  it('passes through the quality of a full TM match', async () => {
    GET.mockResolvedValueOnce({
      value: ['Click Me'],
      properties: { title: ['Tip'] },
      sources: ['translation-memory'],
      quality: 100,
    });

    const result = await fetchComposedMachinery(
      1,
      locale,
      'translation-memory',
    );

    expect(result[0].quality).toBe(100);
  });

  it('returns empty array when response is empty', async () => {
    GET.mockResolvedValueOnce({});
    const result = await fetchComposedMachinery(
      1,
      locale,
      'translation-memory',
    );
    expect(result).toEqual([]);
  });

  it('falls back to the requested service when sources is missing', async () => {
    GET.mockResolvedValueOnce({
      value: ['composed'],
    });

    const result = await fetchComposedMachinery(
      1,
      locale,
      'microsoft-translator',
    );

    expect(result[0].sources).toEqual(['microsoft-translator']);
  });
});
