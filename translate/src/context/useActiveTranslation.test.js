import { useContext } from 'react';
import { vi } from 'vitest';
import { useActiveTranslation } from './EntityView';

vi.mock('react', async (importOriginal) => {
  const actual = await importOriginal();
  return { ...actual, useContext: vi.fn(), useMemo: (cb) => cb() };
});

describe('useActiveTranslation', () => {
  afterAll(() => {
    vi.restoreAllMocks();
  });

  it('returns the correct string', () => {
    vi.mocked(useContext).mockReturnValue({
      entity: { translation: { string: 'world' } },
    });
    const res = useActiveTranslation();
    expect(res).toEqual({ string: 'world' });
  });

  it('does not return rejected translations', () => {
    vi.mocked(useContext).mockReturnValue({
      entity: { translation: { string: 'world', status: 'rejected' } },
    });
    const res = useActiveTranslation();
    expect(res).toBeNull();
  });
});
