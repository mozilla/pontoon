import React, { useContext, useEffect } from 'react';
import { render } from '@testing-library/react';
import { vi } from 'vitest';

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
        initMentions('sl', 42);
      }, []);
      return null;
    };

    render(
      <MentionUsersProvider>
        <Trigger />
      </MentionUsersProvider>,
    );

    expect(fetchUsersList).toHaveBeenCalledWith('sl', 42);
  });
});
