import * as hookModule from '~/hooks/useTranslator';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { InteractiveTour } from './InteractiveTour';
import { vi } from 'vitest';

beforeAll(() => {
  vi.mock('~/hooks/useTranslator', () => ({
    useTranslator: vi.fn(() => false),
  }));

  vi.mock('reactour', () => ({
    default: ({ isOpen }) => (isOpen ? <div data-testid='mock-tour' /> : null),
  }));
});
afterAll(() => hookModule.useTranslator.mockRestore());

describe('<InteractiveTour>', () => {
  it('renders correctly on the tutorial page for unauthenticated user', () => {
    const store = createReduxStore({
      project: { slug: 'tutorial' },
      user: { isAuthenticated: false },
    });
    const { getByTestId } = mountComponentWithStore(InteractiveTour, store);

    getByTestId('mock-tour');
  });

  it('does not render on non-tutorial page', () => {
    const store = createReduxStore({
      project: { slug: 'firefox' },
      user: { isAuthenticated: false },
    });
    const { queryByTestId } = mountComponentWithStore(InteractiveTour, store);

    expect(queryByTestId('mock-tour')).not.toBeInTheDocument();
  });

  it('does not render if the user has already seen the tutorial', () => {
    const store = createReduxStore({
      project: { slug: 'tutorial' },
      user: { tourStatus: -1 },
    });
    const { queryByTestId } = mountComponentWithStore(InteractiveTour, store);

    expect(queryByTestId('mock-tour')).not.toBeInTheDocument();
  });
});
