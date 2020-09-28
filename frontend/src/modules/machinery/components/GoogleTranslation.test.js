import React from 'react';
import { shallow } from 'enzyme';

import GoogleTranslation from './GoogleTranslation';

describe('<GoogleTranslation>', () => {
    it('renders the GoogleTranslation component properly', () => {
        const wrapper = shallow(<GoogleTranslation />);

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized').props().id).toEqual(
            'machinery-GoogleTranslation--visit-google',
        );
        expect(wrapper.find('li a').props().href).toContain(
            'https://translate.google.com/',
        );
        expect(wrapper.find('li a').props().title).toContain(
            'Visit Google Translate',
        );
        expect(wrapper.find('li a span').text()).toEqual('Google Translate');
    });
});
