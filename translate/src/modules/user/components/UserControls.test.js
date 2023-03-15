import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { SignIn } from './SignIn';
import { UserControls } from './UserControls';

jest.mock('./UserAutoUpdater', () => ({ UserAutoUpdater: () => null }));

describe('<UserControls>', () => {
  it('shows a Sign in link when user is logged out', () => {
    const store = createReduxStore({
      user: { isAuthenticated: false, notifications: {} },
    });
    const wrapper = mountComponentWithStore(UserControls, store);

    expect(wrapper.find(SignIn)).toHaveLength(1);
  });

  it('hides a Sign in link when user is logged in', () => {
    const store = createReduxStore({
      user: { isAuthenticated: true, notifications: {} },
    });
    const wrapper = mountComponentWithStore(UserControls, store);

    expect(wrapper.find(SignIn)).toHaveLength(0);
  });
});
