import React from 'react';
import { mount } from 'enzyme';
import each from 'jest-each';

import createMarker from 'lib/react-content-marker';

import pythonFormattingVariable from './pythonFormattingVariable';


describe('pythonFormattingVariable', () => {
    each([
        ['%%', '100%% correct'],
        ['%(number)d', 'There were %(number)d cows'],
        ['%(cows.number)d', 'There were %(cows.number)d cows'],
        ['%(number of cows)d', 'There were %(number of cows)d cows'],
        ['%(number)03d', 'There were %(number)03d cows'],
        ['%(number) 3d', 'There were %(number) 3d cows'],
        ['%(number)*d', 'There were %(number)*d cows'],
        ['%(number)3.1d', 'There were %(number)3.1d cows'],
        ['%(number)Ld', 'There were %(number)Ld cows'],
    ])
    .it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([pythonFormattingVariable]);
        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
