import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import jsonPlaceholder from './jsonPlaceholder';

describe('jsonPlaceholder', () => {
    each([
        ['$USER$', 'Hello $USER$'],
        ['$USER1$', 'Hello $USER1$'],
        ['$FIRST_NAME$', 'Hello $FIRST_NAME$'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([jsonPlaceholder]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });

    each([['$user$', 'Hello $user$'], ['Hello $USER'], ['Hello USER$']]).it(
        'does not mark anything in `%s`',
        (content) => {
            const Marker = createMarker([jsonPlaceholder]);
            const wrapper = shallow(<Marker>{content}</Marker>);
            expect(wrapper.find('mark')).toHaveLength(0);
        },
    );
});
