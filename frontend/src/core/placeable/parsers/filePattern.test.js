import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import filePattern from './filePattern';


describe('filePattern', () => {
    each([
        ['/home/lisa', 'Hello /home/lisa'],
        ['~/user', 'Hello ~/user'],
        ['/home/homer/budget.md', 'The money is in /home/homer/budget.md'],
    ])
    .it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([filePattern]);
        const wrapper = shallow(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
