import React, { useContext, useEffect } from 'react';
import { render } from '@testing-library/react';
import { vi } from 'vitest';

import { Location } from './Location';
import { MentionUsers, MentionUsersProvider } from './MentionUsers';
import { fetchUsersList } from '~/api/user';

vi.mock('~/api/user', () => ({
  fetchUsersList: vi.fn(() => Promise.resolve([])),
}));

describe('MentionUsersProvider', () => {
  it('fetches users with locale and project from Location context', () => {
    const Trigger = () => {
      const { initMentions } = useContext(MentionUsers);
      useEffect(() => {
        initMentions();
      }, []);
      return null;
    };

    render(
      <Location.Provider value={{ locale: 'sl', project: 'pontoon-test' }}>
        <MentionUsersProvider>
          <Trigger />
        </MentionUsersProvider>
      </Location.Provider>,
    );

    expect(fetchUsersList).toHaveBeenCalledWith('sl', 'pontoon-test');
  });
});
