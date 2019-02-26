import React from 'react';
import { mount } from 'enzyme';

import createMarker from 'lib/react-content-marker';

import escapeSequence from './escapeSequence';


describe('escapeSequence', () => {
    it('marks the right parts of a string', () => {
        const Marker = createMarker([escapeSequence]);
        const content = 'hello,\\tworld';

        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('\\');
    });
});
