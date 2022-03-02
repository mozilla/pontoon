import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import qtFormatting from './qtFormatting';

describe('qtFormatting', () => {
    each([
        ['%1', 'Hello, %1'],
        ['%99', 'Hello, %99'],
        ['%L1', 'Hello, %L1'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([qtFormatting]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
