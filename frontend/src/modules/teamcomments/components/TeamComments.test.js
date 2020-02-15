import React from 'react';
import { shallow } from 'enzyme';

import TeamComments from './TeamComments';

describe('<TeamComments>', () => {
    const DEFAULT_USER = 'AndyDwyer';

    it('shows correct message when no comments', () => {
        const teamComments = {
            entity: 267,
            comments: [],
        };

        const wrapper = shallow(<TeamComments
            teamComments={ teamComments }
            user={ DEFAULT_USER }
        />);

        expect(wrapper.find('p').text()).toEqual('No comments available.');
    });
});
