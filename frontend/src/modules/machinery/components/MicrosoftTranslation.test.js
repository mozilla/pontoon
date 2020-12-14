import React from 'react';
import { shallow } from 'enzyme';

import MicrosoftTranslation from './MicrosoftTranslation';

describe('<MicrosoftTranslation>', () => {
    it('renders the MicrosoftTranslation component properly', () => {
        const wrapper = shallow(<MicrosoftTranslation />);

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized').props().id).toEqual(
            'machinery-MicrosoftTranslation--visit-bing',
        );
        expect(wrapper.find('li a').props().href).toContain(
            'https://www.bing.com/translator',
        );
        expect(wrapper.find('li a').props().title).toContain(
            'Visit Microsoft Translator',
        );
        expect(wrapper.find('li a span').text()).toEqual(
            'MICROSOFT TRANSLATOR',
        );
    });
});
