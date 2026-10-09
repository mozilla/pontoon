import React from 'react';
import userEvent from '@testing-library/user-event';

import { EntityView } from '~/context/EntityView';
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
  beforeAll(() => {
    // needed when the contactPerson mention places the cursor
    Range.prototype.getBoundingClientRect = () => ({});
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

  it('adds contact person mention with url from project contact', async () => {
    const onAddComment = vi.fn();
    const store = createReduxStore();
    const entity = {
      project: {
        contact: { name: 'Leslie_Knope', url: '/contributors/leslie/' },
      },
    };
    const Wrapper = () => (
      <EntityView.Provider value={{ entity }}>
        <AddComment
          user={USER}
          contactPerson='Leslie_Knope'
          onAddComment={onAddComment}
        />
      </EntityView.Provider>
    );
    const { container } = mountComponentWithStore(Wrapper, store);

    await userEvent.click(container.querySelector('.submit-button'));

    expect(onAddComment).toHaveBeenCalledWith(
      expect.stringContaining(
        '<a href="/contributors/leslie/">Leslie_Knope</a>',
      ),
    );
  });
});
