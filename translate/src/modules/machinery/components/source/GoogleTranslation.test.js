import React from 'react';
import { shallow } from 'enzyme';

import { GoogleTranslation } from './GoogleTranslation';

describe('<GoogleTranslation>', () => {
  it('renders the GoogleTranslation component properly', () => {
    const mockTranslation = {
      translation: 'Translated text here',
      original: 'Original text here',
    };

    const wrapper = shallow(
      <GoogleTranslation translation={mockTranslation} />,
    );

    expect(wrapper.find('li')).toHaveLength(1);
    expect(wrapper.find('Localized').props().id).toEqual(
      'machinery-GoogleTranslation--translation-source',
    );
    expect(wrapper.find('span.translation-source')).toHaveLength(1);
    expect(
      wrapper.find('span.translation-source').props().onClick,
    ).toBeDefined();
    expect(wrapper.find('span.translation-source span').text()).toEqual(
      'GOOGLE TRANSLATE',
    );
  });
});
