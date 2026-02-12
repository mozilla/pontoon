import React from 'react';

import { MentionUsers } from '~/context/MentionUsers';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { AddComment } from './AddComment';
import { vi } from 'vitest';
import { fireEvent } from '@testing-library/react';

const USER = {
  user: 'RSwanson',
  username: 'Ron_Swanson',
  imageURL: '',
};

describe('<AddComment>', () => {
  it('calls submitComment function', () => {
    const store = createReduxStore();
    const submitCommentFn = vi.fn();
    const Wrapper = () => (
      <MentionUsers.Provider
        value={{ initMentions: vi.fn(), mentionUsers: [] }}
      >
        <AddComment onAddComment={submitCommentFn} user={USER} />
      </MentionUsers.Provider>
    );
    const wrapper = mountComponentWithStore(Wrapper, store);

    fireEvent.click(wrapper.queryByRole('button'));
    expect(submitCommentFn.calledOnce).toBeTruthy;
  });

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
