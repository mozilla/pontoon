import React from 'react';

import { UserAutoUpdater } from './UserAutoUpdater';
import { vi } from 'vitest';
import { render } from '@testing-library/react';

describe('<UserAutoUpdater>', () => {
  it('fetches user data on mount', () => {
    const getUserData = vi.fn();
    render(<UserAutoUpdater getUserData={getUserData} />);

    expect(getUserData).toHaveBeenCalledOnce();
  });

  it('fetches user data every 2 minutes', () => {
    vi.useFakeTimers();

    const getUserData = vi.fn();
    render(<UserAutoUpdater getUserData={getUserData} />);

    vi.advanceTimersByTime(2 * 60 * 1000);
    expect(getUserData).toHaveBeenCalledTimes(2);

    vi.advanceTimersByTime(2 * 60 * 1000);
    expect(getUserData).toHaveBeenCalledTimes(3);

    // If less than 2 minutes have passed, it doesn't trigger.
    vi.advanceTimersByTime(60 * 1000);
    expect(getUserData).toHaveBeenCalledTimes(3);
  });
});
