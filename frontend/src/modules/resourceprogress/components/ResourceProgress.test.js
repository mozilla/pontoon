import React from 'react';
import { shallow } from 'enzyme';

import { ResourceProgressBase } from './ResourceProgress';


describe('<ResourceProgress>', () => {
    const STATS = {
        approved: 5,
        fuzzy: 4,
        unreviewed: 5,
        warnings: 3,
        errors: 2,
        missing: 1,
        total: 15,
    };

    it('shows only a selector by default', () => {
        const wrapper = shallow(<ResourceProgressBase stats={ STATS } />);

        expect(wrapper.find('.selector').exists()).toBeTruthy();
        expect(wrapper.find('.menu').exists()).toBeFalsy();
    });

    it('shows the info menu after a click', () => {
        const wrapper = shallow(<ResourceProgressBase stats={ STATS } />);
        wrapper.find('.selector').simulate('click');

        expect(wrapper.find('.menu').exists()).toBeTruthy();
    });
});
