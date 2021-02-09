import React from 'react';
import { shallow } from 'enzyme';

import createMarker from 'react-content-marker';

import tabCharacter from './tabCharacter';

describe('tabCharacter', () => {
    it('marks the right parts of a string', () => {
        const Marker = createMarker([tabCharacter]);
        const content = 'hello,\tworld';

        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('\u2192');
    });
});
