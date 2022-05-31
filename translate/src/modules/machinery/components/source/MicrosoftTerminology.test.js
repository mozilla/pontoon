import { mount } from 'enzyme';
import React from 'react';

import { Locale } from '~/context/Locale';

import { MockLocalizationProvider } from '~/test/utils';

import { MicrosoftTerminology } from './MicrosoftTerminology';

const LOCALE = { msTerminologyCode: 'en-US' };
const PROPS = {
  original: 'A horse, a horse! My kingdom for a horse',
};

describe('<MicrosoftTerminology>', () => {
  it('renders the MicrosoftTerminology component properly', () => {
    const wrapper = mount(
      <Locale.Provider value={LOCALE}>
        <MockLocalizationProvider>
          <MicrosoftTerminology original={PROPS.original} />
        </MockLocalizationProvider>
      </Locale.Provider>,
    );

    expect(wrapper.find('li')).toHaveLength(1);
    expect(wrapper.find('Localized').props().id).toEqual(
      'machinery-MicrosoftTerminology--visit-microsoft',
    );
    expect(wrapper.find('li a').props().href).toContain(
      'https://www.microsoft.com/Language/en-US/Search.aspx?sString=' +
        PROPS.original +
        '&langID=' +
        LOCALE.msTerminologyCode,
    );
    expect(wrapper.find('li a').props().title).toContain(
      'Visit Microsoft Terminology Service API.',
    );
    expect(wrapper.find('li a span').text()).toEqual('MICROSOFT');
  });
});
