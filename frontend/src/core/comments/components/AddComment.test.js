import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import AddComment from './AddComment';

const DEFAULT_USER = {
    user: 'RSwanson',
    username: 'Ron_Swanson',
    imageURL: '',
};

const USERS = {
    users: {
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
            <AddComment
                {...DEFAULT_USER}
                {...USERS}
                submitComment={submitCommentFn}
            />,
        );

        const event = {
            preventDefault: sinon.spy(),
        };

        wrapper.find('button').simulate('onClick', event);
        expect(submitCommentFn.calledOnce).toBeTruthy;
    });
});
