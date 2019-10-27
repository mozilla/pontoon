import React from 'react';
import { shallow } from 'enzyme';

import MicrosoftTerminology from './MicrosoftTerminology';


describe('<MicrosoftTerminology>', () => {
    it('renders the MicrosoftTerminology component properly', () => {
        const source = {
            type: 'microsoft-terminology',
            url: 'https://www.microsoft.com/Language/en-US/Search.aspx?sString=',
        };

        const wrapper = shallow(<MicrosoftTerminology
            source={ source }
        />);

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized').props().id).toEqual('machinery-MicrosoftTerminology--visit-microsoft');
        expect(wrapper.find('li a').props().href).toContain(source.url);
        expect(wrapper.find('li a').props().title).toContain('Visit Microsoft Terminology Service API.');
        expect(wrapper.find('li a span').text()).toEqual('Microsoft');
    });
});
