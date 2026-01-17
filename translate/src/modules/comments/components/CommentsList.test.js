import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { CommentsList } from './CommentsList';
import { vi } from 'vitest';

vi.mock('react-time-ago', () => {
  return {
    default: () => null,
  };
});

describe('<CommentsList>', () => {
  const DEFAULT_USER = 'AnnPerkins';

  const DEFAULT_TRANSLATION = {
    user: '',
    username: '',
    gravatarURLSmall: '',
  };

  it('shows the correct number of comments', () => {
    const store = createReduxStore();
    const { container } = mountComponentWithStore(CommentsList, store, {
      translation: {
        ...DEFAULT_TRANSLATION,
        comments: [
          { id: 1, content: '11', userBanner: '' },
          { id: 2, content: '22', userBanner: '' },
          { id: 3, content: '33', userBanner: '' },
        ],
      },
      user: DEFAULT_USER,
    });

    expect(container.querySelectorAll('ul > *')).toHaveLength(3);
  });
});
