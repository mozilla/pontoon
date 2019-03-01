import React from 'react';
import { mount } from 'enzyme';

import createMarker from 'lib/react-content-marker';

import tabCharacter from './tabCharacter';


describe('tabCharacter', () => {
    it('marks the right parts of a string', () => {
        const Marker = createMarker([tabCharacter]);
        const content = 'hello,\tworld';

        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('\u2192');
    });
});
