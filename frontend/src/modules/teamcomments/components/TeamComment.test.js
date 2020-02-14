import React from 'react';
import { shallow } from 'enzyme';

import TeamComment from './TeamComment';

describe('<TeamComment>', () => {
    const DEFAULT_USER = 'AndyDwyer';

    it('shows correct message when no comments', () => {
        const teamComments = {
            entity: 267,
            comments: [],
        };

        const wrapper = shallow(<TeamComment
            teamComments={ teamComments }
            user={ DEFAULT_USER }
        />);

        expect(wrapper.find('p').text()).toEqual('No comments available.');
    });
});
