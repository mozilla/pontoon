import React from 'react';
import { shallow } from 'enzyme';

import createMarker from 'react-content-marker';

import escapeSequence from './escapeSequence';

describe('escapeSequence', () => {
    it('marks the right parts of a string', () => {
        const Marker = createMarker([escapeSequence]);
        const content = 'hello,\\tworld';

        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('\\');
    });
});
