import React from 'react';
import { mount } from 'enzyme';

import createMarker from 'lib/react-content-marker';

import pythonFormatString from './pythonFormatString';


describe('pythonFormatString', () => {
    it('marks the right parts of a string', () => {
        const Marker = createMarker([pythonFormatString]);
        const content = `hello, {0}`;

        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('{0}');
    });
});
