import React from 'react';
import { shallow } from 'enzyme';

import MicrosoftTerminology from './MicrosoftTerminology';


const PROPS = {
    sourceString: 'A horse, a horse! My kingdom for a horse',
    localeCode: 'en-US',
};

describe('<MicrosoftTerminology>', () => {
    it('renders the MicrosoftTerminology component properly', () => {
        const wrapper = shallow(<MicrosoftTerminology
            sourceString = { PROPS.sourceString }
            localeCode = { PROPS.localeCode }
        />);

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized').props().id).toEqual('machinery-MicrosoftTerminology--visit-microsoft');
        expect(wrapper.find('li a').props().href).toContain(
            'https://www.microsoft.com/Language/en-US/Search.aspx?sString='+
            PROPS.sourceString + '&langID=' + PROPS.localeCode
        );
        expect(wrapper.find('li a').props().title).toContain('Visit Microsoft Terminology Service API.');
        expect(wrapper.find('li a span').text()).toEqual('Microsoft');
    });
});
