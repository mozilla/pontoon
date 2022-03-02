import React from 'react';
import { shallow } from 'enzyme';

import createMarker from 'react-content-marker';

import altAttribute from './altAttribute';

describe('altAttribute', () => {
    it('marks the right parts of a string', () => {
        const Marker = createMarker([altAttribute]);
        const content = 'alt="hello"';

        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('alt="hello"');
    });
});
