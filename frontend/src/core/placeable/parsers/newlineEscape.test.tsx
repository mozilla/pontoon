import React from 'react';
import { shallow } from 'enzyme';

import createMarker from 'react-content-marker';

import newlineEscape from './newlineEscape';

describe('newlineEscape', () => {
    it('marks the right parts of a string', () => {
        const Marker = createMarker([newlineEscape]);
        const content = '\\n';

        const wrapper = shallow(<Marker>{content}</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('\\n');
    });
});
