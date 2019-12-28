import React from 'react';
import { shallow } from 'enzyme';

import CommentsList from './CommentsList';

describe('<CommentsList>', () => {
    it('shows the correct number of comments', () => {
        const comments = [
                { id: 1 },
                { id: 2 },
                { id: 3 },
            ];

        const wrapper = shallow(<CommentsList comments={ comments } />);

        expect(wrapper.find('ul > *')).toHaveLength(3);
    });
});