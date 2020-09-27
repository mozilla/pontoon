import React from 'react';
import createMarker from 'react-content-marker';
import { shallow } from 'enzyme';
import each from 'jest-each';

import fluentString from './fluentString';

describe('fluentString', () => {
    each([
        ['{""}', 'Hello {""}'],
        ['{ "" }', 'Hello { "" }'],
        ['{ "world!" }', 'Hello { "world!" }'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([fluentString]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });

    each([
        [
            '{ "hello!" }',
            '{ "world!" }',
            'Hello { "hello!" } from { "world!" }',
        ],
    ]).it('marks `%s` and `%s` in `%s`', (mark1, mark2, content) => {
        const Marker = createMarker([fluentString]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(2);
        expect(wrapper.find('mark').at(0).text()).toEqual(mark1);
        expect(wrapper.find('mark').at(1).text()).toEqual(mark2);
    });
});
