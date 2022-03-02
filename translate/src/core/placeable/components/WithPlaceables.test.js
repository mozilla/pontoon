import React from 'react';
import { shallow } from 'enzyme';

import WithPlaceables from './WithPlaceables';

describe('Test parser order', () => {
    it('matches JSON placeholder', () => {
        const content = 'You have created $COUNT$ aliases';
        const wrapper = shallow(<WithPlaceables>{content}</WithPlaceables>);

        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toContain('$COUNT$');
    });
});
