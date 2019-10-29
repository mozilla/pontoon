import React from 'react';
import { shallow } from 'enzyme';

import TransvisionMemory from './TransvisionMemory';


const PROPS = {
    sourceString: 'A horse, a horse! My kingdom for a horse',
    localeCode: 'en-US',
};

describe('<TransvisionMemory>', () => {
    it('renders the TransvisionMemory component properly', () => {
        const wrapper = shallow(<TransvisionMemory
            sourceString = { PROPS.sourceString }
            localeCode = { PROPS.localeCode }
        />);

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized').props().id).toEqual('machinery-TransvisionMemory--visit-transvision');
        expect(wrapper.find('li a').props().href).toContain(
            'https://transvision.mozfr.org/?repo=global' +
            '&recherche=' + encodeURIComponent(PROPS.sourceString) +
            '&locale=' + PROPS.localeCode
        );
        expect(wrapper.find('li a').props().title).toContain('Visit Transvision');
        expect(wrapper.find('li a span').text()).toEqual('Mozilla');
    });
});
