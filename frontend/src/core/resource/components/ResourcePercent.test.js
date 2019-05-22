import React from 'react';
import { shallow } from 'enzyme';

import ResourcePercent from './ResourcePercent';


describe('<ResourcePercent>', () => {
    const RESOURCE = {
        approved_strings: 2,
        strings_with_warnings: 3,
        total_strings: 10,
    };

    it('renders correctly', () => {
        const wrapper = shallow(<ResourcePercent resource={ RESOURCE } />);
        expect(wrapper.find('.percent').text()).toEqual('50%');
    });
});
