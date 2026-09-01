import { usePluralExamples } from './usePluralExamples';
import { afterAll, describe, expect, it, vi } from 'vitest';

vi.mock('react', async (importOriginal) => {
  const actual = await importOriginal();
  return { ...actual, useMemo: (cb) => cb() };
});

describe('usePluralExamples', () => {
  afterAll(() => {
    vi.restoreAllMocks();
  });

  it('returns a map of Slovenian plural examples', () => {
    using consoleErrorSpy = vi.spyOn(console, 'error');
    const res = usePluralExamples({
      cldrPlurals: [1, 2, 3, 5],
      pluralRule:
        '(n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || n%100==4 ? 2 : 3)',
    });

    expect(res).toEqual({ 1: 1, 2: 2, 3: 3, 5: 0 });
    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });

  it('prevents infinite loop if locale plurals are not configured properly', () => {
    using consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => {});
    const res = usePluralExamples({
      cldrPlurals: [0, 1, 2, 3, 4, 5],
      pluralRule: '(n != 1)',
    });

    expect(res).toEqual({ 0: 1, 1: 0 });
    expect(consoleErrorSpy).toHaveBeenCalledOnce();
  });

  it('uses 0 as an example rather than skipping the category', () => {
    using consoleErrorSpy = vi.spyOn(console, 'error');
    // Romanian: `few` covers 0 and 1..19, so its first example is 0
    const res = usePluralExamples({
      cldrPlurals: [1, 3, 5],
      pluralRule: '(n==1 ? 0 : (n==0 || (n%100 > 0 && n%100 < 20)) ? 1 : 2)',
    });

    expect(res).toEqual({ 1: 1, 3: 0, 5: 20 });
    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });

  it('finds an example for the CLDR many category of millions', () => {
    using consoleErrorSpy = vi.spyOn(console, 'error');
    // Breton: `many` only matches non-zero multiples of a million
    const res = usePluralExamples({
      cldrPlurals: [1, 2, 3, 4, 5],
      pluralRule:
        '(n % 10 == 1 && n % 100 != 11 && n % 100 != 71 && n % 100 != 91) ? 0 : ((n % 10 == 2 && n % 100 != 12 && n % 100 != 72 && n % 100 != 92) ? 1 : ((((n % 10 == 3 || n % 10 == 4) || n % 10 == 9) && (n % 100 < 10 || n % 100 > 19) && (n % 100 < 70 || n % 100 > 79) && (n % 100 < 90 || n % 100 > 99)) ? 2 : ((n != 0 && n % 1000000 == 0) ? 3 : 4)))',
    });

    expect(res).toEqual({ 1: 1, 2: 2, 3: 3, 4: 1000000, 5: 0 });
    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });

  it('reports a locale whose plural rule yields fewer forms than it declares', () => {
    using consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => {});
    // A rule that can only ever return 0 or 1 cannot fill three categories
    const res = usePluralExamples({
      cldrPlurals: [0, 1, 5],
      pluralRule: '(n != 1)',
    });

    expect(res).toEqual({ 0: 1, 1: 0 });
    expect(consoleErrorSpy).toHaveBeenCalledOnce();
  });
});
