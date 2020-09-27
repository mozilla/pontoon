import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import xmlTag from './xmlTag';

describe('xmlTag', () => {
    each([
        ['<user>', 'hello, <user>John'],
        ['</user>', 'hello, </user>'],
        ['<user name="John">', 'hello, <user name="John">'],
        ["<user name='John'>", "hello, <user name='John'>"],
        ["<user data-name='John'>", "hello, <user data-name='John'>"],
        ['<User.Birthday>', 'Happy <User.Birthday>!'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([xmlTag]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
