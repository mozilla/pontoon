import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import pythonFormattingVariable from './pythonFormattingVariable';

describe('pythonFormattingVariable', () => {
    each([
        ['%%', '100%% correct'],
        ['%s', 'There were %s'],
        ['%(number)d', 'There were %(number)d cows'],
        ['%(cows.number)d', 'There were %(cows.number)d cows'],
        ['%(number of cows)d', 'There were %(number of cows)d cows'],
        ['%(number)03d', 'There were %(number)03d cows'],
        ['%(number)*d', 'There were %(number)*d cows'],
        ['%(number)3.1d', 'There were %(number)3.1d cows'],
        ['%(number)Ld', 'There were %(number)Ld cows'],
        ['%s', 'path/to/file_%s.png'],
        ['%s', 'path/to/%sfile.png'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([pythonFormattingVariable]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });

    each([
        ['10 % complete'],
        // We used to match '%(number) 3d' here, but don't anymore to avoid
        // false positives.
        // See https://bugzilla.mozilla.org/show_bug.cgi?id=1251186
        ['There were %(number) 3d cows'],
    ]).it('does not mark anything in `%s`', (content) => {
        const Marker = createMarker([pythonFormattingVariable]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(0);
    });
});
