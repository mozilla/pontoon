import React from 'react';
import { shallow } from 'enzyme';

import CommentsList from './CommentsList';

describe('<CommentsList>', () => {
    const DEFAULT_USER = 'AndyDwyer';

    const DEFAULT_TRANSLATION = {
        user: '',
        username: '',
        gravatarURLSmall: '',
    }

    it('shows the correct number of comments', () => {
        const comments = [
                { id: 1 },
                { id: 2 },
                { id: 3 },
            ];

        const wrapper = shallow(<CommentsList
            comments={ comments }
            user={ DEFAULT_USER }
            isTranslator={ true }
            translation={ DEFAULT_TRANSLATION }
        />);

        expect(wrapper.find('ul > *')).toHaveLength(3);
    });

    it('shows the correct number of team comments', () => {
        const teamComments = {
            entity: 267,
            comments: [
                { id: 1 },
                { id: 2 },
                { id: 3 },
            ],
        };

        const wrapper = shallow(<CommentsList
            teamComments={ teamComments }
            user={ DEFAULT_USER }
        />);

        expect(wrapper.find('ul > *')).toHaveLength(3);
    });

    it('shows correct message when no team comments', () => {
        const teamComments = {
            entity: 267,
            comments: [],
        };

        const wrapper = shallow(<CommentsList
            teamComments={ teamComments }
            user={ DEFAULT_USER }
        />);

        expect(wrapper.find('p').text()).toEqual('No comments available.');
    });
});
