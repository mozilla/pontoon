import React from 'react';
import { mount } from 'enzyme';

import { SearchTerms } from './SearchTerms';

describe('SearchTerms', () => {
  it('does not break on regexp special characters', () => {
    const wrapper = mount(
      <SearchTerms search='(bar'>{'foo (bar)'}</SearchTerms>,
    );
    expect(wrapper.find('mark').text()).toEqual('(bar');
  });
});
