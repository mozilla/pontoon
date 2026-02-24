import React from 'react';

import { MentionUsers } from '~/context/MentionUsers';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { AddComment } from './AddComment';
import { vi } from 'vitest';

const USER = {
  user: 'RSwanson',
  username: 'Ron_Swanson',
  imageURL: '',
};

describe('<AddComment>', () => {
  it('fetches mentionable users on render', () => {
    const initMentions = vi.fn();
    const store = createReduxStore();
    const Wrapper = () => (
      <MentionUsers.Provider value={{ initMentions, mentionUsers: [] }}>
        <AddComment user={USER} />
      </MentionUsers.Provider>
    );
    mountComponentWithStore(Wrapper, store);

    expect(initMentions).toHaveBeenCalledOnce();
  });
});
