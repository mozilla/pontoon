import React from 'react';
import { shallow } from 'enzyme';

import Comment from './Comment';


describe('<Comment>', () => {
    const DEFAULT_COMMENT = {
        author: '',
        username: '',
        userGravatarUrlSmall: '',
        createdAt: '',
        dateIso: '',
        content: "What I hear when I'm being yelled at is people caring loudly at me.",
        translation: 0,
        id: 1,
    }

    it('returns a link for the author', () => {
        const comments = {
            ...DEFAULT_COMMENT,
            ...{ username: 'Leslie_Knope', author: 'LKnope' }
        };
        const wrapper = shallow(<Comment
            comment={ comments }
            key={ comments.id }
        />);

        const link = wrapper.find('a');
        expect(link).toHaveLength(1);
        expect(link.at(0).props().children).toEqual('LKnope');
        expect(link.at(0).props().href).toEqual('/contributors/Leslie_Knope');
    });
});
