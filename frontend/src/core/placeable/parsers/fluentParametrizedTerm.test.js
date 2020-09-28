import React from 'react';
import createMarker from 'react-content-marker';
import { shallow } from 'enzyme';
import each from 'jest-each';

import fluentParametrizedTerm from './fluentParametrizedTerm';

describe('fluentParametrizedTerm', () => {
    each([
        ['{-brand(case: "test")}', 'Hello {-brand(case: "test")}'],
        [
            '{ -brand(case: "what ever") }',
            'Hello { -brand(case: "what ever") }',
        ],
        [
            '{ -brand-name(foo-bar: "now that\'s a value!") }',
            'Hello { -brand-name(foo-bar: "now that\'s a value!") }',
        ],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([fluentParametrizedTerm]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });

    each([
        [
            '{-brand(case: "test")}',
            '{-vendor(case: "right")}',
            'Hello {-brand(case: "test")} and {-vendor(case: "right")}',
        ],
    ]).it('marks `%s` and `%s` in `%s`', (mark1, mark2, content) => {
        const Marker = createMarker([fluentParametrizedTerm]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(2);
        expect(wrapper.find('mark').at(0).text()).toEqual(mark1);
        expect(wrapper.find('mark').at(1).text()).toEqual(mark2);
    });
});
