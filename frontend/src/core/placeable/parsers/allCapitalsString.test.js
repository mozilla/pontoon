import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'lib/react-content-marker';

import allCapitalsString from './allCapitalsString';


describe('allCapitalsString', () => {
    each([
        ['HTML', 'Use the HTML page'],
        ['GTK+', 'In GTK+'],
        ['GNOME', 'GNOME-stuff'],
        ['XDG_USER_DIRS', 'with XDG_USER_DIRS'],
    ])
    .it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([allCapitalsString]);
        const wrapper = shallow(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });

    each([
        ['I am'],
        ['Use the A4 paper'],
    ])
    .it('does not mark anything in `%s`', (content) => {
        const Marker = createMarker([allCapitalsString]);
        const wrapper = shallow(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(0);
    });
});
