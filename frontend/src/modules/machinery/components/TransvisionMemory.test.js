import React from 'react';
import { shallow } from 'enzyme';

import TransvisionMemory from './TransvisionMemory';

const PROPS = {
    original: 'A horse, a horse! My kingdom for a horse',
    locale: {
        code: 'en-US',
    },
};

describe('<TransvisionMemory>', () => {
    it('renders the TransvisionMemory component properly', () => {
        const wrapper = shallow(
            <TransvisionMemory
                original={PROPS.original}
                locale={PROPS.locale}
            />,
        );

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized').props().id).toEqual(
            'machinery-TransvisionMemory--visit-transvision',
        );
        expect(wrapper.find('li a').props().href).toContain(
            'https://transvision.mozfr.org/?repo=global' +
                '&recherche=' +
                encodeURIComponent(PROPS.original) +
                '&locale=' +
                PROPS.locale.code,
        );
        expect(wrapper.find('li a').props().title).toContain(
            'Visit Transvision',
        );
        expect(wrapper.find('li a span').text()).toEqual('Mozilla');
    });
});
