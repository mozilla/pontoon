import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import shortCapitalNumberString from './shortCapitalNumberString';

describe('shortCapitalNumberString', () => {
    each([
        ['3D', '3D'],
        ['A4', 'Use the A4 paper'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([shortCapitalNumberString]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });

    each([['I am'], ['3d'], ['3DS']]).it(
        'does not mark anything in `%s`',
        (content) => {
            const Marker = createMarker([shortCapitalNumberString]);
            const wrapper = shallow(<Marker>{content}</Marker>);
            expect(wrapper.find('mark')).toHaveLength(0);
        },
    );
});
