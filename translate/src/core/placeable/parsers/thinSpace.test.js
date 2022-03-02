import React from 'react';
import { shallow } from 'enzyme';

import createMarker from 'react-content-marker';

import thinSpace from './thinSpace';

describe('thinSpace', () => {
    it('marks the right parts of a string', () => {
        const Marker = createMarker([thinSpace]);
        const content = 'hello,\u2009world';

        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('\u2009');
    });
});
