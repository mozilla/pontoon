import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import stringFormattingVariable from './stringFormattingVariable';

describe('stringFormattingVariable', () => {
    each([
        ['%d', 'There were %d cows', 1],
        ['%Id', 'There were %Id cows', 1],
        [['%d', '%s'], 'There were %d %s', 2],
        [['%1$s', '%2$s'], '%1$s was kicked by %2$s', 2],
        ['%Id', 'There were %Id cows', 1],
        ["%'f", "There were %'f cows", 1],
        ['%#x', 'There were %#x cows', 1],
        ['%3d', 'There were %3d cows', 1],
        ['%33d', 'There were %33d cows', 1],
        ['%*d', 'There were %*d cows', 1],
        ['%1$d', 'There were %1$d cows', 1],
        [null, 'There were %\u00a0d cows', 0],
    ]).it('marks `%s` in `%s`', (mark, content, matchesNumber) => {
        const Marker = createMarker([stringFormattingVariable]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(matchesNumber);
        if (matchesNumber === 1) {
            expect(wrapper.find('mark').text()).toEqual(mark);
        } else if (matchesNumber > 1) {
            for (let i = 0; i < matchesNumber; i++) {
                expect(wrapper.find('mark').at(i).text()).toEqual(mark[i]);
            }
        }
    });

    each([
        ['10 % complete'],
        // We used to match '% d' here, but don't anymore to avoid
        // false positives.
        // See https://bugzilla.mozilla.org/show_bug.cgi?id=1251186
        ['There were % d cows'],
    ]).it('does not mark anything in `%s`', (content) => {
        const Marker = createMarker([stringFormattingVariable]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(0);
    });
});
