import React from 'react';
import sinon from 'sinon';

import { MentionUsers } from '~/context/MentionUsers';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { AddComment } from './AddComment';

const USER = {
  user: 'RSwanson',
  username: 'Ron_Swanson',
  imageURL: '',
};

describe('<AddComment>', () => {
  it('calls submitComment function', () => {
    const store = createReduxStore();
    const submitCommentFn = sinon.spy();
    const Wrapper = () => (
      <MentionUsers.Provider
        value={{ initMentions: sinon.spy(), mentionUsers: [] }}
      >
        <AddComment onAddComment={submitCommentFn} user={USER} />
      </MentionUsers.Provider>
    );
    const wrapper = mountComponentWithStore(Wrapper, store);

    const event = {
      preventDefault: sinon.spy(),
    };

    wrapper.find('button').simulate('click', event);
    expect(submitCommentFn.calledOnce).toBeTruthy;
  });

  it('fetches mentionable users on render', () => {
    const initMentions = sinon.spy();
    const store = createReduxStore();
    const Wrapper = () => (
      <MentionUsers.Provider value={{ initMentions, mentionUsers: [] }}>
        <AddComment user={USER} />
      </MentionUsers.Provider>
    );
    mountComponentWithStore(Wrapper, store);

    expect(initMentions.calledOnce).toBeTruthy;
  });
});
