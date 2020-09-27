import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import punctuation from './punctuation';

describe('punctuation', () => {
    each([
        ['™', 'Pontoon™'],
        ['℉', '9℉ OMG so cold'],
        ['π', 'She had π cats'],
        ['ʼ', 'Please use the correct quote: ʼ'],
        ['«', 'Here comes the French: «'],
        ['€', 'Gimme the €'],
        ['…', 'Downloading…'],
        ['—', 'Hello — Lisa'],
        ['–', 'Hello – Lisa'],
        [' ', 'Hello\u202Fworld'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([punctuation]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });

    each([['These, are not. Special: punctuation; marks! Or are "they"?']]).it(
        'does not mark anything in `%s`',
        (content) => {
            const Marker = createMarker([punctuation]);
            const wrapper = shallow(<Marker>{content}</Marker>);
            expect(wrapper.find('mark')).toHaveLength(0);
        },
    );
});
