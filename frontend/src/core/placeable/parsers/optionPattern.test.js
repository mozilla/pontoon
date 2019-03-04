import React from 'react';
import { mount } from 'enzyme';
import each from 'jest-each';

import createMarker from 'lib/react-content-marker';

import optionPattern from './optionPattern';


describe('optionPattern', () => {
    each([
        ['--help', 'Type --help for this help'],
        ['-S', 'Short -S ones also'],
    ])
    .it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([optionPattern]);
        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
