import React from 'react';
import { shallow } from 'enzyme';

import CommentsList from './CommentsList';

describe('<CommentsList>', () => {
    const DEFAULT_USER = 'AnnPerkins';

    const DEFAULT_TRANSLATION = {
        user: '',
        username: '',
        gravatarURLSmall: '',
    };

    it('shows the correct number of comments', () => {
        const comments = [{ id: 1 }, { id: 2 }, { id: 3 }];

        const wrapper = shallow(
            <CommentsList
                comments={comments}
                user={DEFAULT_USER}
                isTranslator={true}
                translation={DEFAULT_TRANSLATION}
            />,
        );

        expect(wrapper.find('ul > *')).toHaveLength(3);
    });
});
