import React from 'react';
import { shallow } from 'enzyme';

import createMarker from 'react-content-marker';

import narrowNonBreakingSpace from './narrowNonBreakingSpace';

describe('narrowNonBreakingSpace', () => {
    it('marks the right parts of a string', () => {
        const Marker = createMarker([narrowNonBreakingSpace]);
        const content = 'hello,\u202Fworld';

        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('\u202F');
    });
});
