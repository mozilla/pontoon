import { shallow } from 'enzyme';
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
    const submitCommentFn = sinon.spy();
    const wrapper = shallow(
      <AddComment submitComment={submitCommentFn} user={USER} />,
    );

    const event = {
      preventDefault: sinon.spy(),
    };

    wrapper.find('button').simulate('onClick', event);
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
