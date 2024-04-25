import React from 'react';
import { shallow } from 'enzyme';

import { TranslationMemory } from './TranslationMemory';

describe('<TranslationMemory>', () => {
  it('renders the component without number of occurrences properly', () => {
    const wrapper = shallow(<TranslationMemory />);

    expect(wrapper.find('li')).toHaveLength(1);
    expect(wrapper.find('Localized')).toHaveLength(1);

    expect(wrapper.find('Localized').at(0).props().id).toEqual(
      'machinery-TranslationMemory--translation-source',
    );
    expect(wrapper.find('li .translation-source').text()).toEqual(
      'TRANSLATION MEMORY',
    );
  });

  it('renders the component with number of occurrences properly', () => {
    const wrapper = shallow(<TranslationMemory itemCount={2} />);

    expect(wrapper.find('li')).toHaveLength(1);
    expect(wrapper.find('Localized')).toHaveLength(2);

    expect(wrapper.find('Localized').at(1).props().id).toEqual(
      'machinery-TranslationMemory--number-occurrences',
    );
    expect(wrapper.find('sup').props().title).toEqual(
      'Number of translation occurrences',
    );
    expect(wrapper.find('sup').text()).toContain('2');
  });
});
