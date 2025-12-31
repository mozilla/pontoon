import Tour from 'reactour';

import * as hookModule from '~/hooks/useTranslator';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { InteractiveTour } from './InteractiveTour';
import { vi } from 'vitest';

beforeAll(() => {
  vi.mock('~/hooks/useTranslator', () => ({
    useTranslator: vi.fn(() => false),
  }));
});
afterAll(() => hookModule.useTranslator.mockRestore());

describe('<InteractiveTour>', () => {
  it('renders correctly on the tutorial page for unauthenticated user', () => {
    const store = createReduxStore({
      project: { slug: 'tutorial' },
      user: { isAuthenticated: false },
    });
    const wrapper = mountComponentWithStore(InteractiveTour, store);

    expect(wrapper.find(Tour)).toHaveLength(1);
  });

  it('does not render on non-tutorial page', () => {
    const store = createReduxStore({
      project: { slug: 'firefox' },
      user: { isAuthenticated: false },
    });
    const wrapper = mountComponentWithStore(InteractiveTour, store);

    expect(wrapper.find(Tour)).toHaveLength(0);
  });

  it('does not render if the user has already seen the tutorial', () => {
    const store = createReduxStore({
      project: { slug: 'tutorial' },
      user: { tourStatus: -1 },
    });
    const wrapper = mountComponentWithStore(InteractiveTour, store);

    expect(wrapper.find(Tour)).toHaveLength(0);
  });
});
