import React from 'react';
import { shallow } from 'enzyme';

import createMarker from 'react-content-marker';

import nonBreakingSpace from './nonBreakingSpace';

describe('nonBreakingSpace', () => {
    it('marks the right parts of a string', () => {
        const Marker = createMarker([nonBreakingSpace]);
        const content = 'hello,\u00A0world';

        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('\u00A0');
    });
});
