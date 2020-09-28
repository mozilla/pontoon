import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import WithPlaceablesForFluent from './WithPlaceablesForFluent';

describe('<WithPlaceablesForFluent>', () => {
    each([
        ['Fluent string expression', '{"world"}', 'Hello {"world"}'],
        ['Fluent term', '{ -brand-name }', 'Hello { -brand-name }'],
        [
            'Fluent parametrized term',
            '{ -count($items) }',
            'We have { -count($items) } things',
        ],
        [
            'Fluent function',
            '{ COUNT(items: []) }',
            'I have { COUNT(items: []) } things',
        ],
    ]).it('matches a %s', (type, mark, content) => {
        const wrapper = shallow(
            <WithPlaceablesForFluent>{content}</WithPlaceablesForFluent>,
        );

        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toContain(mark);
    });
});
