import React from 'react';
import { shallow } from 'enzyme';
import each from 'jest-each';

import { MachineryTranslationSource } from './MachineryTranslationSource';

const DEFAULT_TRANSLATION = {
  sources: ['translation-memory'],
};

describe('<MachineryTranslationSource>', () => {
  each([
    ['translation-memory', 'TranslationMemory'],
    ['google-translate', 'GoogleTranslation'],
    ['microsoft-translator', 'MicrosoftTranslation'],
    ['microsoft-terminology', 'MicrosoftTerminology'],
    ['caighdean', 'CaighdeanTranslation'],
  ]).it('renders `%s` type for `%s` component correctly', (type, component) => {
    const translation = {
      sources: [type],
    };
    const wrapper = shallow(
      <MachineryTranslationSource translation={translation} />,
    );

    expect(wrapper.find(component)).toHaveLength(1);
  });

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
