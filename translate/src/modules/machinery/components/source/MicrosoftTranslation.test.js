import React from 'react';
import { shallow } from 'enzyme';

import { MicrosoftTranslation } from './MicrosoftTranslation';

describe('<MicrosoftTranslation>', () => {
  it('renders the MicrosoftTranslation component properly', () => {
    const wrapper = shallow(<MicrosoftTranslation />);

    expect(wrapper.find('li')).toHaveLength(1);
    expect(wrapper.find('Localized').props().id).toEqual(
      'machinery-MicrosoftTranslation--translation-source',
    );
    expect(wrapper.find('li span').text()).toEqual('MICROSOFT TRANSLATOR');
  });
});
