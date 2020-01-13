import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import AddComment from './AddComment';

describe('<AddComment>', () => {
    it('calls submitComment function', () => {
        const submitCommentFn = sinon.spy();
        const wrapper = shallow(<AddComment
            submitComment={ submitCommentFn }
        />);

        wrapper.prop('onSubmit') === submitCommentFn;
    });
});
