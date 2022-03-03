import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import AddComment from './AddComment';

const USER = {
  user: {
    user: 'RSwanson',
    username: 'Ron_Swanson',
    imageURL: '',
    users: [
      {
        name: 'April Ludwig',
        url: 'aprilL@parksdept.com',
        display: 'April',
      },
    ],
  },
};

describe('<AddComment>', () => {
  it('calls submitComment function', () => {
    const submitCommentFn = sinon.spy();
    const wrapper = shallow(
      <AddComment {...USER} submitComment={submitCommentFn} />,
    );

    const event = {
      preventDefault: sinon.spy(),
    };

    wrapper.find('button').simulate('onClick', event);
    expect(submitCommentFn.calledOnce).toBeTruthy;
  });
});
