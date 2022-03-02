import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import pythonFormatString from './pythonFormatString';

describe('pythonFormatString', () => {
    each([
        ['{0}', 'hello, {0}'],
        ['{name}', 'hello, {name}'],
        ['{name!s}', 'hello, {name!s}'],
        ['{someone.name}', 'hello, {someone.name}'],
        ['{name[0]}', 'hello, {name[0]}'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([pythonFormatString]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
