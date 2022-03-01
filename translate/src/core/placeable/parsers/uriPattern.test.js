import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import uriPattern from './uriPattern';

describe('uriPattern', () => {
    each([
        ['http://example.org/'],
        ['https://example.org/'],
        ['ftp://example.org/'],
        ['nttp://example.org/'],
        ['file://example.org/'],
        ['irc://example.org/'],
        ['www.example.org/'],
        ['ftp.example.org/'],
        ['http://example.org:8888'],
        ['http://example.org:8888/?'],
        ['http://example.org/path/to/resource?var1=$@3!?%=iwdu8'],
        ['http://example.org/path/to/resource?var1=$@3!?%=iwdu8&var2=bar'],
        ['HTTP://EXAMPLE.org/'],
    ]).it('correctly marks URI `%s`', (uri) => {
        const Marker = createMarker([uriPattern]);
        const wrapper = shallow(<Marker>{uri}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(uri);
    });
});
