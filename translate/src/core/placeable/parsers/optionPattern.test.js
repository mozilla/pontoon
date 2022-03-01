import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import optionPattern from './optionPattern';

describe('optionPattern', () => {
    each([
        ['--help', 'Type --help for this help'],
        ['-S', 'Short -S ones also'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([optionPattern]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
