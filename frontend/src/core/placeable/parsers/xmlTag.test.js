import React from 'react';
import { mount } from 'enzyme';
import each from 'jest-each';

import createMarker from 'lib/react-content-marker';

import xmlTag from './xmlTag';


describe('xmlTag', () => {
    each([
        ['<user>', 'hello, <user>John'],
        ['</user>', 'hello, </user>'],
        ['<user name="John">', 'hello, <user name="John">'],
        ["<user name='John'>", "hello, <user name='John'>"],
        ['<User.Birthday>', 'Happy <User.Birthday>!'],
    ])
    .it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([xmlTag]);
        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
