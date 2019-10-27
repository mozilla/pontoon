import React from 'react';
import { shallow } from 'enzyme';

import MicrosoftTranslation from './MicrosoftTranslation';


describe('<MicrosoftTranslation>', () => {
    it('renders the component properly', () => {
        const source = {
            type: 'microsoft-translator',
            url: 'https://www.bing.com/translator',
        };

        const wrapper = shallow(<MicrosoftTranslation
            source={ source }
        />);

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized').props().id).toEqual('machinery-MicrosoftTranslation--visit-bing');
        expect(wrapper.find('li a').props().href).toContain(source.url);
        expect(wrapper.find('li a').props().title).toContain('Visit Bing Translate');
        expect(wrapper.find('li a span').text()).toEqual('Microsoft Translator');
    });
});
