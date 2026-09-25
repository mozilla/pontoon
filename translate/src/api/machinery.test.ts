import type { Locale } from '~/context/Locale';

import {
  fetchComposedMachinery,
  fetchOpenAIComposedTranslation,
  fetchOpenAITranslation,
} from './machinery';
import * as base from './utils/base';

vi.mock('./utils/base', () => ({
  GET: vi.fn(),
  POST: vi.fn(() => Promise.resolve({ translation: 'resultado' })),
}));

vi.mock('./utils/csrfToken', () => ({
  getCSRFToken: vi.fn(() => 'test-csrf-token'),
}));

describe('fetchOpenAITranslation', () => {
  const POST = vi.mocked(base.POST);
  const references = { 'google-translate': ['hola'] };

  it('sends required params', async () => {
    await fetchOpenAITranslation('hello', references, 'informal', 'es');

    const [url, params] = POST.mock.calls[0] as [string, URLSearchParams];
    expect(url).toBe('/openai-chatgpt/');
    expect(params.get('english_text')).toBe('hello');
    expect(params.get('references')).toBe(JSON.stringify(references));
    expect(params.get('characteristic')).toBe('informal');
    expect(params.get('locale')).toBe('es');
  });

  it('defaults to the manual trigger', async () => {
    await fetchOpenAITranslation('hello', references, 'informal', 'es');

    const [, params] = POST.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('trigger')).toBe('manual');
  });

  it('sends the auto trigger when given', async () => {
    await fetchOpenAITranslation(
      'hello',
      references,
      'rephrased',
      'es',
      42,
      'auto',
    );

    const [, params] = POST.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('trigger')).toBe('auto');
  });

  it('serializes an empty reference set', async () => {
    await fetchOpenAITranslation('hello', {}, 'informal', 'es');

    const [, params] = POST.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('references')).toBe('{}');
  });

  it('omits entity_pk when not provided', async () => {
    await fetchOpenAITranslation('hello', references, 'informal', 'es');

    const [, params] = POST.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('entity_pk')).toBeNull();
  });

  it('includes entity_pk when provided', async () => {
    await fetchOpenAITranslation('hello', references, 'informal', 'es', 42);

    const [, params] = POST.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('entity_pk')).toBe('42');
  });

  it('returns the translation from the response', async () => {
    const result = await fetchOpenAITranslation(
      'hello',
      references,
      'informal',
      'es',
    );

    expect(result).toEqual([
      {
        sources: ['openai-chatgpt'],
        original: 'hello',
        translation: 'resultado',
      },
    ]);
  });

  it('returns empty array when response has no translation', async () => {
    POST.mockResolvedValueOnce({});
    const result = await fetchOpenAITranslation(
      'hello',
      references,
      'informal',
      'es',
    );
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

describe('fetchOpenAIComposedTranslation', () => {
  const POST = vi.mocked(base.POST);
  const value = ['Hola'];
  const properties = { title: ['Sugerencia'] };
  const refined = { value: ['Saludos'], properties: { title: ['Refinada'] } };

  beforeEach(() => {
    POST.mockResolvedValue(refined);
  });

  it('sends the whole composed model', async () => {
    await fetchOpenAIComposedTranslation(42, value, properties, 'formal', 'es');

    const [url, params] = POST.mock.calls[0] as [string, URLSearchParams];
    expect(url).toBe('/openai-chatgpt-composed/');
    expect(params.get('entity_pk')).toBe('42');
    expect(params.get('value')).toBe(JSON.stringify(value));
    expect(params.get('properties')).toBe(JSON.stringify(properties));
    expect(params.get('characteristic')).toBe('formal');
    expect(params.get('locale')).toBe('es');
    expect(params.get('trigger')).toBe('manual');
    expect(params.get('csrfmiddlewaretoken')).toBe('test-csrf-token');
  });

  it('sends an empty object for an entity without properties', async () => {
    await fetchOpenAIComposedTranslation(42, value, undefined, 'formal', 'es');

    const [, params] = POST.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('properties')).toBe('{}');
  });

  it('passes the automatic trigger through', async () => {
    await fetchOpenAIComposedTranslation(
      42,
      value,
      properties,
      'rephrased',
      'es',
      'auto',
    );

    const [, params] = POST.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('trigger')).toBe('auto');
  });

  it('returns the refined model', async () => {
    const result = await fetchOpenAIComposedTranslation(
      42,
      value,
      properties,
      'formal',
      'es',
    );
    expect(result).toEqual(refined);
  });

  it('returns null when there was nothing to refine', async () => {
    POST.mockResolvedValueOnce({});
    const result = await fetchOpenAIComposedTranslation(
      42,
      value,
      properties,
      'formal',
      'es',
    );
    expect(result).toBeNull();
  });

  it('returns null when the request fails', async () => {
    POST.mockRejectedValueOnce(new Error('boom'));
    vi.spyOn(console, 'error').mockImplementation(() => {});
    const result = await fetchOpenAIComposedTranslation(
      42,
      value,
      properties,
      'formal',
      'es',
    );
    expect(result).toBeNull();
  });
});
