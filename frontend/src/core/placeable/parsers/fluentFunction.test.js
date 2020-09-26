import React from 'react';
import createMarker from 'react-content-marker';
import { shallow } from 'enzyme';
import each from 'jest-each';

import fluentFunction from './fluentFunction';

describe('fluentFunction', () => {
    each([
        ['{COPY()}', 'Hello {COPY()}'],
        ['{ DATETIME($date) }', 'Hello { DATETIME($date) }'],
        [
            '{ NUMBER($ratio, minimumFractionDigits: 2) }',
            'Hello { NUMBER($ratio, minimumFractionDigits: 2) }',
        ],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([fluentFunction]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });

    each([
        [
            '{ DATETIME($date) }',
            '{ COPY() }',
            'Hello { DATETIME($date) } and { COPY() }',
        ],
    ]).it('marks `%s` and `%s` in `%s`', (mark1, mark2, content) => {
        const Marker = createMarker([fluentFunction]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(2);
        expect(wrapper.find('mark').at(0).text()).toEqual(mark1);
        expect(wrapper.find('mark').at(1).text()).toEqual(mark2);
    });
});
