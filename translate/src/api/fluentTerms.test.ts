import { fetchFluentTerms } from './fluentTerms';
import * as base from './utils/base';

import type { FluentTerms } from './fluentTerms';

vi.mock('./utils/base', () => ({
  GET: vi.fn(),
}));

describe('fetchFluentTerms', () => {
  const GET = vi.mocked(base.GET);

  const project = 'acme';
  const locale = 'ab';
  const sample: FluentTerms = {
    '-brand-name': {
      value: ['about Brand'],
      properties: { foo: ['Foo'] },
      translation_value: ['Markari buruz'],
      translation_properties: null,
    },
    '-other-term': {
      value: ['Other'],
      properties: null,
      translation_value: null,
      translation_properties: null,
    },
  };

  afterEach(() => {
    GET.mockReset();
  });

  it('sends required params', async () => {
    GET.mockResolvedValue(sample);

    await fetchFluentTerms(project, locale);

    const [url, params] = GET.mock.calls[0] as [string, URLSearchParams];
    expect(url).toBe('/get-fluent-terms/');
    expect(params.get('project')).toBe(project);
    expect(params.get('locale')).toBe(locale);
  });

  it('returns the term map unchanged', async () => {
    GET.mockResolvedValue(sample);

    const result = await fetchFluentTerms(project, locale);

    expect(result).toBe(sample);
  });

  it('propagates request errors', async () => {
    GET.mockRejectedValue(new Error('Bad Request'));

    await expect(fetchFluentTerms(project, locale)).rejects.toThrow(
      'Bad Request',
    );
  });
});
