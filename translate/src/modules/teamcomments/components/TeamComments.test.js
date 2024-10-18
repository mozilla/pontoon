import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { TeamComments } from './TeamComments';

jest.mock('react-time-ago', () => () => null);

describe('<TeamComments>', () => {
  const DEFAULT_USER = 'AndyDwyer';

  it('shows correct message when no comments', () => {
    const store = createReduxStore();
    const wrapper = mountComponentWithStore(TeamComments, store, {
      teamComments: { entity: 267, comments: [] },
      user: DEFAULT_USER,
    });

    expect(wrapper.find('p').text()).toEqual('No comments available.');
  });

  it('renders correctly when there are comments', () => {
    const store = createReduxStore();
    const wrapper = mountComponentWithStore(TeamComments, store, {
      teamComments: {
        entity: 267,
        comments: [
          { id: 1, content: '11', userStatus: '' },
          { id: 2, content: '22', userStatus: '' },
          { id: 3, content: '33', userStatus: '' },
        ],
      },
      user: DEFAULT_USER,
    });

    expect(wrapper.children()).toHaveLength(1);
    expect(wrapper.find('li')).toHaveLength(3);
  });
});
