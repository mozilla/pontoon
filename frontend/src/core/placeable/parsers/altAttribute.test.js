import React from 'react';
import { mount } from 'enzyme';

import createMarker from 'lib/react-content-marker';

import altAttribute from './altAttribute';


describe('altAttribute', () => {
    it('marks the right parts of a string', () => {
        const Marker = createMarker([altAttribute]);
        const content = 'alt="hello"';

        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('alt="hello"');
    });
});
