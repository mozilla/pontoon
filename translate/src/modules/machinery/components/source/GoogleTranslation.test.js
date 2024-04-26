import React from 'react';
import { shallow } from 'enzyme';

import { GoogleTranslation } from './GoogleTranslation';

describe('<GoogleTranslation>', () => {
  it('renders the GoogleTranslation component properly', () => {
    const wrapper = shallow(<GoogleTranslation />);

    expect(wrapper.find('li')).toHaveLength(1);
    expect(wrapper.find('Localized').props().id).toEqual(
      'machinery-GoogleTranslation--translation-source',
    );
    expect(wrapper.find('li span').text()).toEqual('GOOGLE TRANSLATE');
  });

  it('renders the GoogleTranslation LLM features properly', () => {
    const mockTranslation = {
      translation: 'Translated text here',
      original: 'Original text here',
    };

    const wrapper = shallow(
      <GoogleTranslation
        isOpenAIChatGPTSupported={true}
        translation={mockTranslation}
      />,
    );

    expect(wrapper.find('li')).toHaveLength(1);
    expect(wrapper.find('.selector Localized').props().id).toEqual(
      'machinery-GoogleTranslation--translation-source',
    );
    expect(wrapper.find('span.translation-source')).toHaveLength(1);
    expect(wrapper.find('.selector').props().onClick).toBeDefined();
    expect(wrapper.find('span.translation-source').text()).toEqual(
      'GOOGLE TRANSLATE',
    );
  });
});
