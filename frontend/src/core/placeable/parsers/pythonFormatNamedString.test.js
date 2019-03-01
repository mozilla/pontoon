import React from 'react';
import { mount } from 'enzyme';
import each from 'jest-each';

import createMarker from 'lib/react-content-marker';

import pythonFormatNamedString from './pythonFormatNamedString';


describe('pythonFormatNamedString', () => {
    each([
        ['%(name)s', 'Hello %(name)s'],
        ['%(number)d', 'Rolling %(number)d dices'],
        ['%(name)S', 'Hello %(name)S'],
        ['%(number)D', 'Rolling %(number)D dices'],
    ])
    .it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([pythonFormatNamedString]);
        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
