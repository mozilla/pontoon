import React from 'react';
import { mount } from 'enzyme';

import createMarker from 'lib/react-content-marker';

import narrowNonBreakingSpace from './narrowNonBreakingSpace';


describe('narrowNonBreakingSpace', () => {
    it('marks the right parts of a string', () => {
        const Marker = createMarker([narrowNonBreakingSpace]);
        const content = `hello,\u202Fworld`;

        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('\u202F');
    });
});
