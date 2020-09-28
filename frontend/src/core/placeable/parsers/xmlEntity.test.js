import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import xmlEntity from './xmlEntity';

describe('xmlEntity', () => {
    each([
        ['&brandShortName;', 'Welcome to &brandShortName;'],
        ['&#1234;', 'hello, &#1234;'],
        ['&xDEAD;', 'hello, &xDEAD;'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([xmlEntity]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
