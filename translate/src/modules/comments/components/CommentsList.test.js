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
    const comments = [
      { id: 1, content: '11', userBanner: '' },
      { id: 2, content: '22', userBanner: '' },
      { id: 3, content: '33', userBanner: '' },
    ];
    const { getByText } = mountComponentWithStore(CommentsList, store, {
      translation: {
        ...DEFAULT_TRANSLATION,
        comments,
      },
      user: DEFAULT_USER,
    });

    for (const comment of comments) {
      getByText(comment.content);
    }
  });
});
