import { vi } from 'vitest';
import * as Hooks from '~/hooks';
import { useReadonlyEditor } from './useReadonlyEditor';
import { useContext } from 'react';

beforeAll(() => {
  vi.mock('react', async (importOriginal) => {
    const actual = await importOriginal();
    return {
      ...actual,
      useContext: vi.fn(),
    };
  });
  vi.spyOn(Hooks, 'useAppSelector');
});

afterAll(() => {
  vi.restoreAllMocks();
});

function fakeSelector(readonly, isAuthenticated) {
  vi.mocked(useContext).mockReturnValue({
    entity: { pk: 42, original: 'hello', readonly },
  });
  return (cb) => cb({ user: { isAuthenticated } });
}

describe('useReadonlyEditor', () => {
  it('returns true if user not authenticated', () => {
    vi.mocked(Hooks.useAppSelector).mockImplementation(
      fakeSelector(false, false),
    );
    expect(useReadonlyEditor()).toBe(true);
  });

  it('returns true if entity read-only', () => {
    vi.mocked(Hooks.useAppSelector).mockImplementation(
      fakeSelector(true, true),
    );
    expect(useReadonlyEditor()).toBe(true);
  });

  it('returns false If entity not read-only and user authenticated', () => {
    vi.mocked(Hooks.useAppSelector).mockImplementation(
      fakeSelector(false, true),
    );
    expect(useReadonlyEditor()).toBe(false);
  });
});
