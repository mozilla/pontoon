import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import unusualSpace from './unusualSpace';

describe('unusualSpace', () => {
    each([
        [' ', 'hello world '],
        [' ', 'hello\n world'],
        ['  ', 'hello  world'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([unusualSpace]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
