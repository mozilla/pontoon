import React from 'react';
import { mount } from 'enzyme';

import createMarker from 'lib/react-content-marker';

import multipleSpaces from './multipleSpaces';


describe('multipleSpaces', () => {
    it('marks the right parts of a string', () => {
        const Marker = createMarker([multipleSpaces]);
        const content = `hello,   world`;

        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(' \u00B7 ');
    });
});
