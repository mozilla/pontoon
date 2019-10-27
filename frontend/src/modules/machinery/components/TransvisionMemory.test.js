import React from 'react';
import { shallow } from 'enzyme';

import TransvisionMemory from './TransvisionMemory';


describe('<TransvisionMemory>', () => {
    it('renders the component properly', () => {
        const source = {
            type: 'transvision',
            url: 'https://transvision.mozfr.org/?repo=global',
        };

        const wrapper = shallow(<TransvisionMemory
            source={ source }
        />);

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized').props().id).toEqual('machinery-TransvisionMemory--visit-transvision');
        expect(wrapper.find('li a').props().href).toContain(source.url);
        expect(wrapper.find('li a').props().title).toContain('Visit Transvision');
        expect(wrapper.find('li a span').text()).toEqual('Mozilla');
    });
});
