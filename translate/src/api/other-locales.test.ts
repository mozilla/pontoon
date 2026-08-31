import { fetchAllLocales } from './other-locales';
import { GET } from './utils/base';

vi.mock('./utils/base', () => ({
  GET: vi.fn(),
}));

describe('fetchAllLocales', () => {
  afterEach(() => {
    vi.mocked(GET).mockReset();
  });

  describe('all-projects', () => {
    it('hits the global locale list endpoint, not a project endpoint', async () => {
      vi.mocked(GET).mockResolvedValueOnce({ results: [], next: null });

      await fetchAllLocales();

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

      const result = await fetchAllLocales();

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
      const result = await fetchAllLocales();
      expect(result).toEqual([{ code: 'a', name: 'A' }]);
    });
  });
});
