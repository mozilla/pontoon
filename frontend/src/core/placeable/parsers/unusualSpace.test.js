import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'lib/react-content-marker';

import unusualSpace from './unusualSpace';


describe('unusualSpace', () => {
    each([
        [' ', ' hello'],
        [' ', 'hello '],
        [' ', 'hello,\n world'],
        ['  ', 'hello,  beautiful world'],
    ])
    .it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([unusualSpace]);
        const wrapper = shallow(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
