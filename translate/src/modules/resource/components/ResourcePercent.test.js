import React from 'react';
import { shallow } from 'enzyme';

import { ResourcePercent } from './ResourcePercent';

describe('<ResourcePercent>', () => {
  const RESOURCE = {
    approvedStrings: 2,
    pretranslatedStrings: 1,
    stringsWithWarnings: 2,
    totalStrings: 10,
  };

  it('renders correctly', () => {
    const wrapper = shallow(<ResourcePercent resource={RESOURCE} />);
    expect(wrapper.find('.percent').text()).toEqual('50%');
  });
});
