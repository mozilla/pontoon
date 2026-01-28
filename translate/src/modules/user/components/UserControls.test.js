import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { UserControls } from './UserControls';
import { vi, expect } from 'vitest';
import { screen } from '@testing-library/react';

vi.mock('./UserAutoUpdater', () => ({ UserAutoUpdater: () => null }));

describe('<UserControls>', () => {
  it('shows a Sign in link when user is logged out', () => {
    const store = createReduxStore({
      user: { isAuthenticated: false, notifications: {} },
    });
    mountComponentWithStore(UserControls, store);

    expect(screen.queryByTestId('sign-in')).toBeInTheDocument();
  });

  it('hides a Sign in link when user is logged in', () => {
    const store = createReduxStore({
      user: { isAuthenticated: true, notifications: {} },
    });
    mountComponentWithStore(UserControls, store);

    expect(screen.queryByTestId('sign-in')).not.toBeInTheDocument();
  });
});
