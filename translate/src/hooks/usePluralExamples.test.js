import { usePluralExamples } from './usePluralExamples';
import { vi } from 'vitest';

describe('usePluralExamples', () => {
  beforeAll(() => {
    vi.mock('react', async (importOriginal) => {
      const actual = await importOriginal();
      return {
        ...actual,
        useMemo: (cb) => cb(),
      };
    });
  });

  afterAll(() => {
    vi.restoreAllMocks();
  });

  it('returns a map of Slovenian plural examples', () => {
    const consoleErrorSpy = vi.spyOn(console, 'error');
    const res = usePluralExamples({
      cldrPlurals: [1, 2, 3, 5],
      pluralRule:
        '(n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || n%100==4 ? 2 : 3)',
    });

    expect(res).toEqual({ 1: 1, 2: 2, 3: 3, 5: 0 });
    expect(consoleErrorSpy).toHaveBeenCalledTimes(0);
  });

  it('prevents infinite loop if locale plurals are not configured properly', () => {
    const consoleErrorSpy = vi.spyOn(console, 'error');
    const res = usePluralExamples({
      cldrPlurals: [0, 1, 2, 3, 4, 5],
      pluralRule: '(n != 1)',
    });

    expect(res).toEqual({ 0: 1, 1: 2 });
    expect(consoleErrorSpy).toHaveBeenCalledTimes(1);
  });
});
