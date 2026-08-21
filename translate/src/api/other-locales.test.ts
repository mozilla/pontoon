import { fetchAllLocales } from './other-locales';
import { GET } from './utils/base';

vi.mock('./utils/base', () => ({
  GET: vi.fn(),
}));

describe('fetchAllLocales', () => {
  afterEach(() => {
    vi.mocked(GET).mockReset();
  });

  describe('single project', () => {
    it('fetches the project detail endpoint with the correct slug and fields param', async () => {
      vi.mocked(GET).mockResolvedValueOnce({ localizations: [] });

      await fetchAllLocales('terminology');

      expect(GET).toHaveBeenCalledTimes(1);
      expect(GET).toHaveBeenCalledWith(
        expect.stringMatching(/^\/api\/v2\/projects\/terminology\/\?/),
      );
      expect(GET).toHaveBeenCalledWith(
        expect.stringContaining('fields=localizations'),
      );
    });

    it('extracts locale from the nested localizations shape, not the raw locales field', async () => {
      vi.mocked(GET).mockResolvedValueOnce({
        localizations: [
          { locale: { code: 'de', name: 'German' }, total_strings: 100 },
          { locale: { code: 'fr', name: 'French' }, total_strings: 50 },
        ],
      });

      const result = await fetchAllLocales('terminology');

      expect(result).toEqual([
        { code: 'de', name: 'German' },
        { code: 'fr', name: 'French' },
      ]);
      expect(result[0]).toHaveProperty('name');
    });

    it('returns an empty array if localizations is missing entirely', async () => {
      vi.mocked(GET).mockResolvedValueOnce({});
      const result = await fetchAllLocales('terminology');
      expect(result).toEqual([]);
    });

    it('does not paginate for a single project (only calls GET once)', async () => {
      vi.mocked(GET).mockResolvedValueOnce({
        localizations: [{ locale: { code: 'de', name: 'German' } }],
        next: '/api/v2/projects/terminology/?page=2', 
      });

      await fetchAllLocales('terminology');
      expect(GET).toHaveBeenCalledTimes(1);
    });
  });

  describe('all-projects', () => {
    it('hits the global locale list endpoint, not a project endpoint', async () => {
      vi.mocked(GET).mockResolvedValueOnce({ results: [], next: null });

      await fetchAllLocales('all-projects');

      expect(GET).toHaveBeenCalledWith(
        expect.stringMatching(/^\/api\/v2\/locales\/\?/),
      );

      expect(GET).not.toHaveBeenCalledWith(
        expect.stringContaining('/api/v2/projects/'),
      );
    });

    it('follows pagination until next is null', async () => {
      vi.mocked(GET)
        .mockResolvedValueOnce({
          results: [{ code: 'a', name: 'Locale A' }],
          next: '/api/v2/locales/?page=2',
        })
        .mockResolvedValueOnce({
          results: [{ code: 'b', name: 'Locale B' }],
          next: null,
        });

      const result = await fetchAllLocales('all-projects');

      expect(GET).toHaveBeenCalledTimes(2);
      expect(result).toEqual([
        { code: 'a', name: 'Locale A' },
        { code: 'b', name: 'Locale B' },
      ]);
    });

    it('stops looping and does not hang if next is missing rather than null', async () => {
      vi.mocked(GET).mockResolvedValueOnce({
        results: [{ code: 'a', name: 'A' }],
      });
      const result = await fetchAllLocales('all-projects');
      expect(result).toEqual([{ code: 'a', name: 'A' }]);
    });
  });
});

