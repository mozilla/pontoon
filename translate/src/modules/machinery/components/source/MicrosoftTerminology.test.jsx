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
      'machinery-MicrosoftTerminology--translation-source',
    );
    expect(wrapper.find('li span').text()).toEqual('MICROSOFT');
  });
});
