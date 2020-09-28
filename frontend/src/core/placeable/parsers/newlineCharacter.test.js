import React from 'react';
import { shallow } from 'enzyme';

import createMarker from 'react-content-marker';

import newlineCharacter from './newlineCharacter';

describe('newlineCharacter', () => {
    it('marks the right parts of a string', () => {
        const Marker = createMarker([newlineCharacter]);
        const content = `hello,
            world`;

        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('¶\n');
    });
});
