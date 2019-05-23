import React from 'react';
import { shallow } from 'enzyme';

import { InfoPanelBase } from './InfoPanel';


describe('<InfoPanel>', () => {
    const INFO = 'Hello, World!';

    it('shows only a button by default', () => {
        const wrapper = shallow(<InfoPanelBase info={ INFO } />);

        expect(wrapper.find('.button').exists()).toBeTruthy();
        expect(wrapper.find('.panel').exists()).toBeFalsy();
    });

    it('shows the info panel after a click', () => {
        const wrapper = shallow(<InfoPanelBase info={ INFO } />);
        wrapper.find('.button').simulate('click');

        expect(wrapper.find('.panel').exists()).toBeTruthy();
    });
});
