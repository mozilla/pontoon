import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { CommentsList } from './CommentsList';

jest.mock('react-time-ago', () => () => null);

describe('<CommentsList>', () => {
  const DEFAULT_USER = 'AnnPerkins';

  const DEFAULT_TRANSLATION = {
    user: '',
    username: '',
    gravatarURLSmall: '',
  };

  it('shows the correct number of comments', () => {
    const store = createReduxStore();
    const wrapper = mountComponentWithStore(CommentsList, store, {
      translation: {
        ...DEFAULT_TRANSLATION,
        comments: [
          { id: 1, content: '11' },
          { id: 2, content: '22' },
          { id: 3, content: '33' },
        ],
      },
      user: DEFAULT_USER,
    });

    expect(wrapper.find('ul > *')).toHaveLength(3);
  });
});
