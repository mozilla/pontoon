import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { UserControls } from './UserControls';
import { vi } from 'vitest';

vi.mock('./UserAutoUpdater', () => ({ UserAutoUpdater: () => null }));

describe('<UserControls>', () => {
  it('shows a Sign in link when user is logged out', () => {
    const store = createReduxStore({
      user: { isAuthenticated: false, notifications: {} },
    });
    const { getByRole } = mountComponentWithStore(UserControls, store);
    getByRole('button', { name: /sign in/i });
  });

  it('hides a Sign in link when user is logged in', () => {
    const store = createReduxStore({
      user: { isAuthenticated: true, notifications: {} },
    });
    const { queryByRole } = mountComponentWithStore(UserControls, store);

    expect(queryByRole('button', { name: /sign in/i })).not.toBeInTheDocument();
  });
});
