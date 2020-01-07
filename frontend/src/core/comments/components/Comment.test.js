import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

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

    const DEFAULT_USER = {
        username: 'Leslie_Knope',
    };

    const DEFAULT_CANREVIEW = {
        canReview: true,
    }

    it('returns a string', () => {
        const wrapper = shallow(<p>{ DEFAULT_COMMENT.content }</p>);
        expect(wrapper.text()).toEqual(
            "What I hear when I'm being yelled at is people caring loudly at me."
        );
    });

    it('returns a link for the author', () => {
        const deleteMock = sinon.stub();
        const comments = {
            ...DEFAULT_COMMENT,
            ...{ username: 'Leslie_Knope', author: 'LKnope' }
        };
        const wrapper = shallow(<Comment
            comment={ comments }
            key={ comments.id }
            user={ DEFAULT_USER }
            canReview={ DEFAULT_CANREVIEW }
            deleteComment={ deleteMock }
        />);

        const link = wrapper.find('a');
        expect(link).toHaveLength(1);
        expect(link.at(0).props().children).toEqual('LKnope');
        expect(link.at(0).props().href).toEqual('/contributors/Leslie_Knope');
    });

    it('calls delete function', () => {
        const deleteMock = sinon.stub();
        const wrapper = shallow(<Comment
            comment={ DEFAULT_COMMENT }
            key={ DEFAULT_COMMENT.id }
            user={ DEFAULT_USER }
            canReview={ DEFAULT_CANREVIEW }
            deleteComment={ deleteMock }
        />);

        wrapper.find('button').first().simulate('click', { stopPropagation() {} });
        expect(deleteMock.calledOnce).toBeTruthy();
    });
});
