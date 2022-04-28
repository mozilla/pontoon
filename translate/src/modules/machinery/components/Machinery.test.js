import React from 'react';
import { mount, shallow } from 'enzyme';

import { MockLocalizationProvider } from '~/test/utils';

import { Machinery } from './Machinery';

describe('<Machinery>', () => {
  it('shows a search form', () => {
    const machinery = {
      translations: [],
      searchResults: [],
    };
    const wrapper = shallow(<Machinery machinery={machinery} />);

    expect(wrapper.find('.search-wrapper')).toHaveLength(1);
    expect(
      wrapper.find('#machinery-Machinery--search-placeholder'),
    ).toHaveLength(1);
  });

  it('shows the correct number of translations', () => {
    const machinery = {
      translations: [{ original: '1' }, { original: '2' }, { original: '3' }],
      searchResults: [{ original: '4' }, { original: '5' }],
    };
    const wrapper = shallow(<Machinery machinery={machinery} />);

    expect(wrapper.find('Translation')).toHaveLength(5);
  });

  it('renders a reset button if a source string is present', () => {
    const machinery = {
      translations: [],
      searchResults: [],
      searchString: 'test',
    };
    const wrapper = mount(
      <MockLocalizationProvider>
        <Machinery machinery={machinery} />
      </MockLocalizationProvider>,
    );

    expect(wrapper.find('button')).toHaveLength(1);
  });
});
