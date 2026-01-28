import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { TeamComments } from './TeamComments';
import { vi } from 'vitest';

vi.mock('react-time-ago', () => ({ default: () => null }));

describe('<TeamComments>', () => {
  const DEFAULT_USER = 'AndyDwyer';

  it('shows correct message when no comments', () => {
    const store = createReduxStore();
    const { container } = mountComponentWithStore(TeamComments, store, {
      teamComments: { entity: 267, comments: [] },
      user: DEFAULT_USER,
    });

    expect(container.querySelector('p')).toHaveTextContent(
      'No comments available.',
    );
  });

  it('renders correctly when there are comments', () => {
    const store = createReduxStore();
    const { container } = mountComponentWithStore(TeamComments, store, {
      teamComments: {
        entity: 267,
        comments: [
          { id: 1, content: '11', userBanner: '' },
          { id: 2, content: '22', userBanner: '' },
          { id: 3, content: '33', userBanner: '' },
        ],
      },
      user: DEFAULT_USER,
    });

    expect(container.childElementCount).toBe(1);
    expect(container.querySelectorAll('li')).toHaveLength(3);
  });
});
