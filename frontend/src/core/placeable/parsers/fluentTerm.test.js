import React from 'react';
import createMarker from 'react-content-marker';
import { shallow } from 'enzyme';
import each from 'jest-each';

import fluentTerm from './fluentTerm';

describe('fluentTerm', () => {
    each([
        ['{-brand}', 'Hello {-brand}'],
        ['{ -brand }', 'Hello { -brand }'],
        ['{ -brand-name }', 'Hello { -brand-name }'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([fluentTerm]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });

    each([['{-brand}', '{-vendor}', 'Hello {-brand} from {-vendor}']]).it(
        'marks `%s` and `%s` in `%s`',
        (mark1, mark2, content) => {
            const Marker = createMarker([fluentTerm]);
            const wrapper = shallow(<Marker>{content}</Marker>);
            expect(wrapper.find('mark')).toHaveLength(2);
            expect(wrapper.find('mark').at(0).text()).toEqual(mark1);
            expect(wrapper.find('mark').at(1).text()).toEqual(mark2);
        },
    );
});
