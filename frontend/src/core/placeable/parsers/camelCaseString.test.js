import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import camelCaseString from './camelCaseString';

describe('camelCaseString', () => {
    each([
        ['CamelCase', 'Hello CamelCase'],
        ['iPod', 'Hello iPod'],
        ['DokuWiki', 'Hello DokuWiki'],
        ['KBabel', 'Hello KBabel'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([camelCaseString]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });

    each([['_Bug'], ['NOTCAMEL']]).it(
        'does not mark anything in `%s`',
        (content) => {
            const Marker = createMarker([camelCaseString]);
            const wrapper = shallow(<Marker>{content}</Marker>);
            expect(wrapper.find('mark')).toHaveLength(0);
        },
    );
});
