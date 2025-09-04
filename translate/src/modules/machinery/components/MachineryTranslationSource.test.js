import React from 'react';
import { shallow } from 'enzyme';

import { MachineryTranslationSource } from './MachineryTranslationSource';

const DEFAULT_TRANSLATION = {
  sources: ['translation-memory'],
};

describe('<MachineryTranslationSource>', () => {
  for (const [type, component] of [
    ['translation-memory', 'TranslationMemory'],
    ['google-translate', 'GoogleTranslation'],
    ['microsoft-translator', 'MicrosoftTranslation'],
    ['microsoft-terminology', 'MicrosoftTerminology'],
    ['caighdean', 'CaighdeanTranslation'],
  ]) {
    it(`renders ${type} type for ${component} component correctly`, () => {
      const translation = {
        sources: [type],
      };
      const wrapper = shallow(
        <MachineryTranslationSource translation={translation} />,
      );

      expect(wrapper.find(component)).toHaveLength(1);
    });
  }

  it('shows several sources', () => {
    const translation = {
      sources: [...DEFAULT_TRANSLATION.sources, 'microsoft-terminology'],
    };
    const wrapper = shallow(
      <MachineryTranslationSource translation={translation} />,
    );

    expect(wrapper.find('TranslationMemory')).toHaveLength(1);
    expect(wrapper.find('MicrosoftTerminology')).toHaveLength(1);
  });
});
