import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import createMarker from 'react-content-marker';

import javaFormattingVariable from './javaFormattingVariable';

describe('javaFormattingVariable', () => {
    each([
        ['{1,time}', 'At {1,time}'],
        ['{1,date}', 'on {1,date}, '],
        ['{2}', 'there was {2} '],
        ['{0,number,integer}', 'n planet {0,number,integer}.'],
    ]).it('marks `%s` in `%s`', (mark, content) => {
        const Marker = createMarker([javaFormattingVariable]);
        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(mark);
    });
});
