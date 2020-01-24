import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import AddComment from './AddComment';


const DEFAULT_USER = {
    user: 'RSwanson',
    username: 'Ron_Swanson',
    imageURL: '',
}

describe('<AddComment>', () => {
    it('calls submitComment function', () => {
        const submitCommentFn = sinon.spy();
        const wrapper = shallow(<AddComment
            { ...DEFAULT_USER }
            submitComment={ submitCommentFn }
        />);

        const event = {
            preventDefault: sinon.spy(),
        };

        wrapper.find('form').simulate('submit', event);
        expect(submitCommentFn.calledOnce).toBeTruthy;
    });
});
