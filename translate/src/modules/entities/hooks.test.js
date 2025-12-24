import { useContext } from 'react';
import { useNextEntity, usePreviousEntity } from './hooks';
import { vi } from 'vitest';

const ENTITIES = [
  { pk: 1, original: 'hello' },
  { pk: 2, original: 'world' },
  { pk: 3 },
];

beforeAll(() => {
  vi.mock('react', async (importOriginal) => {
    const actual = await importOriginal();
    return {
      ...actual,
      useContext: vi.fn(),
    };
  });

  vi.mock('~/hooks', async (importOriginal) => {
    const actual = await importOriginal();
    return {
      ...actual,
      useAppSelector: (cb) => cb({ entities: { entities: ENTITIES } }),
    };
  });
});

afterAll(() => {
  vi.restoreAllMocks();
});

describe('hooks', () => {
  describe('useNextEntity', () => {
    it('returns the next entity in the list', () => {
      vi.mocked(useContext).mockReturnValue({ entity: ENTITIES[0] });
      expect(useNextEntity()).toBe(ENTITIES[1]);
    });

    it('returns the first entity when the last one is selected', () => {
      vi.mocked(useContext).mockReturnValue({ entity: ENTITIES[2] });
      expect(useNextEntity()).toBe(ENTITIES[0]);
    });

    it('returns null when the current entity does not exist', () => {
      vi.mocked(useContext).mockReturnValue({ entity: { pk: 99 } });
      expect(useNextEntity()).toBeNull();
    });
  });

  describe('usePreviousEntity', () => {
    it('returns the previous entity in the list', () => {
      vi.mocked(useContext).mockReturnValue({ entity: ENTITIES[1] });
      expect(usePreviousEntity()).toBe(ENTITIES[0]);
    });

    it('returns the last entity when the first one is selected', () => {
      vi.mocked(useContext).mockReturnValue({ entity: ENTITIES[0] });
      expect(usePreviousEntity()).toBe(ENTITIES[2]);
    });

    it('returns null when the current entity does not exist', () => {
      vi.mocked(useContext).mockReturnValue({ entity: { pk: 99 } });
      expect(usePreviousEntity()).toBeNull();
    });
  });
});
