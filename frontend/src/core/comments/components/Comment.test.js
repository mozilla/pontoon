import React from 'react';
import { shallow } from 'enzyme';

import Comment from './Comment';


describe('<Comment>', () => {
    const DEFAULT_COMMENTS = {
        author: '',
        username: '',
        userGravatarUrlSmall: '',
        createdAt: '',
        dateIso: '',
        content: 'Comment for testing',
        translation: 0,
        id: 1,
    }

    describe('renderUser', () => {
        it('returns a link for the author', () => {
            const comments = {
                ...DEFAULT_COMMENTS,
                ...{ username: 'id_Sarevok', author: 'Sarevok' }
            };
            const wrapper = shallow(<Comment
                comment={ comments }
                key={ comments.id }
            />);

            const link = wrapper.find('a');
            expect(link).toHaveLength(1);
            expect(link.at(0).props().children).toEqual('Sarevok');
            expect(link.at(0).props().href).toEqual('/contributors/id_Sarevok');
        });
    });
});