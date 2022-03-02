import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import pythonFormatNamedString from './pythonFormatNamedString';

describe('pythonFormatNamedString', () => {
    each([
        ['%(name)s', 'Hello %(name)s'],
        ['%(number)d', 'Rolling %(number)d dices'],
        ['%(name)S', 'Hello %(name)S'],
        ['%(number)D', 'Rolling %(number)D dices'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([pythonFormatNamedString]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
