import { fetchFluentTerms } from './fluentTerms';
import { getFluentTerms, termsCache } from './fluentTermsCache';

import type { FluentTerms } from './fluentTerms';

vi.mock('./fluentTerms', () => ({
  fetchFluentTerms: vi.fn(),
}));

describe('getFluentTerms', () => {
  const project = 'acme';
  const locale = 'ab';
  const sample: FluentTerms = {
    '-some-term': {
      value: ['some term value'],
      properties: null,
      translation_value: null,
      translation_properties: null,
    },
  };

  beforeEach(() => {
    vi.mocked(fetchFluentTerms).mockResolvedValue(sample);
  });

  afterEach(() => {
    vi.mocked(fetchFluentTerms).mockReset();
    termsCache.clear();
  });

  it('should fetch terms only once', async () => {
    const [a, b] = await Promise.all([
      getFluentTerms(project, locale),
      getFluentTerms(project, locale),
    ]);

    expect(fetchFluentTerms).toHaveBeenCalledTimes(1);
    expect(a).toBe(b);
  });

  it('should always fetch when distinct project/locales are provided', async () => {
    await Promise.all([
      getFluentTerms(project, locale),
      getFluentTerms('something', 'else'),
    ]);

    expect(fetchFluentTerms).toHaveBeenCalledTimes(2);
  });

  it('should return the fetched value', async () => {
    const terms = await getFluentTerms(project, locale);

    expect(terms).toBe(sample);
  });
});
