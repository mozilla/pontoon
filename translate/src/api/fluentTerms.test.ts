import {
  createGetFluentTerms,
  fetchFluentTerms,
  termsCache,
} from './fluentTerms';
import * as base from './utils/base';

import type { FluentTerms } from './fluentTerms';

vi.mock('./utils/base', () => ({
  GET: vi.fn(),
}));

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

describe('fetchFluentTerms', () => {
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

describe('createGetFluentTerms', () => {
  beforeEach(() => {
    GET.mockResolvedValue(sample);
  });

  afterEach(() => {
    termsCache.clear();
  });

  it('should fetch terms only once', async () => {
    const getFluentTerms = createGetFluentTerms(project, locale);
    const [a, b] = await Promise.all([getFluentTerms(), getFluentTerms()]);

    expect(GET).toHaveBeenCalledTimes(1);
    expect(a).toBe(b);
  });

  it('should always fetch when distinct project/locales are provided', async () => {
    await Promise.all([
      createGetFluentTerms(project, locale)(),
      createGetFluentTerms('something', 'else')(),
    ]);

    expect(GET).toHaveBeenCalledTimes(2);
  });

  it('should return the fetched value', async () => {
    const terms = await createGetFluentTerms(project, locale)();

    expect(terms).toBe(sample);
  });
});
