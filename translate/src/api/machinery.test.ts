import { fetchGPTTransform } from './machinery';
import * as base from './utils/base';

vi.mock('./utils/base', () => ({
  GET: vi.fn(() => Promise.resolve({ translation: 'resultado' })),
}));

describe('fetchGPTTransform', () => {
  const GET = vi.mocked(base.GET);

  it('sends required params', async () => {
    await fetchGPTTransform('hello', 'hola', 'informal', 'Spanish');

    const [url, params] = GET.mock.calls[0] as [string, URLSearchParams];
    expect(url).toBe('/gpt-transform/');
    expect(params.get('english_text')).toBe('hello');
    expect(params.get('translated_text')).toBe('hola');
    expect(params.get('characteristic')).toBe('informal');
    expect(params.get('locale')).toBe('Spanish');
  });

  it('omits optional params when not provided', async () => {
    await fetchGPTTransform('hello', 'hola', 'informal', 'Spanish');

    const [, params] = GET.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('entity_id')).toBeNull();
    expect(params.get('entity_comment')).toBeNull();
    expect(params.get('group_comment')).toBeNull();
    expect(params.get('resource_comment')).toBeNull();
    expect(params.get('pinned_comments')).toBeNull();
  });

  it('includes entity_id when provided', async () => {
    await fetchGPTTransform(
      'hello',
      'hola',
      'informal',
      'Spanish',
      'msg-id.value',
    );

    const [, params] = GET.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('entity_id')).toBe('msg-id.value');
    expect(params.get('entity_comment')).toBeNull();
  });

  it('includes entity_comment when provided', async () => {
    await fetchGPTTransform(
      'hello',
      'hola',
      'informal',
      'Spanish',
      undefined,
      'Do not translate brand name',
    );

    const [, params] = GET.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('entity_id')).toBeNull();
    expect(params.get('entity_comment')).toBe('Do not translate brand name');
  });

  it('includes both entity_id and entity_comment when provided', async () => {
    await fetchGPTTransform(
      'hello',
      'hola',
      'formal',
      'Spanish',
      'msg-id.aria-label',
      'Tooltip text for the close button',
    );

    const [, params] = GET.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('entity_id')).toBe('msg-id.aria-label');
    expect(params.get('entity_comment')).toBe(
      'Tooltip text for the close button',
    );
  });

  it('includes group_comment when provided', async () => {
    await fetchGPTTransform(
      'hello',
      'hola',
      'informal',
      'Spanish',
      undefined,
      undefined,
      'Navigation section',
    );

    const [, params] = GET.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('group_comment')).toBe('Navigation section');
  });

  it('includes resource_comment when provided', async () => {
    await fetchGPTTransform(
      'hello',
      'hola',
      'informal',
      'Spanish',
      undefined,
      undefined,
      undefined,
      'Main UI file',
    );

    const [, params] = GET.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('resource_comment')).toBe('Main UI file');
  });

  it('omits pinned_comments when not provided', async () => {
    await fetchGPTTransform('hello', 'hola', 'informal', 'Spanish');

    const [, params] = GET.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('pinned_comments')).toBeNull();
  });

  it('includes pinned_comments when provided', async () => {
    await fetchGPTTransform(
      'hello',
      'hola',
      'informal',
      'Spanish',
      undefined,
      undefined,
      undefined,
      undefined,
      ['First note', 'Second note'],
    );

    const [, params] = GET.mock.calls[0] as [string, URLSearchParams];
    expect(JSON.parse(params.get('pinned_comments') as string)).toEqual([
      'First note',
      'Second note',
    ]);
  });

  it('omits terms when not provided', async () => {
    await fetchGPTTransform('hello', 'hola', 'informal', 'Spanish');

    const [, params] = GET.mock.calls[0] as [string, URLSearchParams];
    expect(params.get('terms')).toBeNull();
  });

  it('includes terms when provided', async () => {
    await fetchGPTTransform(
      'hello',
      'hola',
      'informal',
      'Spanish',
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      [
        {
          text: 'browser',
          partOfSpeech: 'noun',
          definition: '',
          usage: '',
          translation: 'navigateur',
          entityId: 1,
        },
      ],
    );

    const [, params] = GET.mock.calls[0] as [string, URLSearchParams];
    expect(JSON.parse(params.get('terms') as string)).toEqual([
      { text: 'browser', part_of_speech: 'noun', translation: 'navigateur' },
    ]);
  });

  it('returns the translation from the response', async () => {
    const result = await fetchGPTTransform(
      'hello',
      'hola',
      'informal',
      'Spanish',
    );

    expect(result).toEqual([
      {
        sources: ['gpt-transform'],
        original: 'hello',
        translation: 'resultado',
      },
    ]);
  });

  it('returns empty array when response has no translation', async () => {
    GET.mockResolvedValueOnce({});
    const result = await fetchGPTTransform(
      'hello',
      'hola',
      'informal',
      'Spanish',
    );
    expect(result).toEqual([]);
  });
});
