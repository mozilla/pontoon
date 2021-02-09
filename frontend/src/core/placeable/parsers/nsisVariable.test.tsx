import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import nsisVariable from './nsisVariable';

describe('nsisVariable', () => {
    each([
        ['$Brand', '$Brand'],
        ['$BrandName', 'Welcome to $BrandName'],
        ['$MyVar13', 'I am $MyVar13'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([nsisVariable]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });

    each([['$10'], ['foo$bar']]).it(
        'does not mark anything in `%s`',
        (content) => {
            const Marker = createMarker([nsisVariable]);
            const wrapper = shallow(<Marker>{content}</Marker>);
            expect(wrapper.find('mark')).toHaveLength(0);
        },
    );
});
