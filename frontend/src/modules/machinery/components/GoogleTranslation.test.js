import React from 'react';
import { shallow } from 'enzyme';

import GoogleTranslation from './GoogleTranslation';


describe('<GoogleTranslation>', () => {
    it('renders the component properly', () => {
        const source = {
            type: 'google-translate',
            url: 'https://translate.google.com/',
        };

        const wrapper = shallow(<GoogleTranslation
            source={ source }
        />);

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized').props().id).toEqual('machinery-GoogleTranslation--visit-google');
        expect(wrapper.find('li a').props().href).toContain(source.url);
        expect(wrapper.find('li a').props().title).toContain('Visit Google Translate');
        expect(wrapper.find('li a span').text()).toEqual('Google Translate');
    });
});
