import React from 'react';
import { mount } from 'enzyme';
import each from 'jest-each';

import createMarker from 'lib/react-content-marker';

import emailPattern from './emailPattern';


describe('emailPattern', () => {
    each([
        ['lisa@example.org', 'Hello lisa@example.org'],
        ['mailto:lisa@name.me', 'Hello mailto:lisa@name.me'],
    ])
    .it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([emailPattern]);
        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
