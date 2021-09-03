import React from 'react';
import { shallow } from 'enzyme';

import MicrosoftTerminology from './MicrosoftTerminology';

const PROPS = {
    original: 'A horse, a horse! My kingdom for a horse',
    locale: {
        msTerminologyCode: 'en-US',
    },
};

describe('<MicrosoftTerminology>', () => {
    it('renders the MicrosoftTerminology component properly', () => {
        const wrapper = shallow(
            <MicrosoftTerminology
                original={PROPS.original}
                locale={PROPS.locale}
            />,
        );

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized').props().id).toEqual(
            'machinery-MicrosoftTerminology--visit-microsoft',
        );
        expect(wrapper.find('li a').props().href).toContain(
            'https://www.microsoft.com/Language/en-US/Search.aspx?sString=' +
                PROPS.original +
                '&langID=' +
                PROPS.locale.msTerminologyCode,
        );
        expect(wrapper.find('li a').props().title).toContain(
            'Visit Microsoft Terminology Service API.',
        );
        expect(wrapper.find('li a span').text()).toEqual('MICROSOFT');
    });
});
