import React from 'react';

import { MachineryTranslationSource } from './MachineryTranslationSource';
import { render } from '@testing-library/react';

import { MockLocalizationProvider } from '~/test/utils';

const DEFAULT_TRANSLATION = {
  sources: ['translation-memory'],
};
const WrapMachineryTranslationSource = (props) => {
  return (
    <MockLocalizationProvider>
      <MachineryTranslationSource {...props} />
    </MockLocalizationProvider>
  );
};
const translationMemoryTitle = 'TRANSLATION MEMORY';
const googleTranslationTitle = 'GOOGLE TRANSLATE';
const microsoftTranslationTitle = 'MICROSOFT TRANSLATOR';
const microsoftTerminologyTitle = 'MICROSOFT';
const caighdeanTranslationTitle = 'CAIGHDEAN';

describe('<MachineryTranslationSource>', () => {
  for (const [type, component, title] of [
    ['translation-memory', 'TranslationMemory', translationMemoryTitle],
    ['google-translate', 'GoogleTranslation', googleTranslationTitle],
    ['microsoft-translator', 'MicrosoftTranslation', microsoftTranslationTitle],
    [
      'microsoft-terminology',
      'MicrosoftTerminology',
      microsoftTerminologyTitle,
    ],
    ['caighdean', 'CaighdeanTranslation', caighdeanTranslationTitle],
  ]) {
    it(`renders ${type} type for ${component} component correctly`, () => {
      const translation = {
        sources: [type],
      };
      const { getByText } = render(
        <WrapMachineryTranslationSource translation={translation} />,
      );

      getByText(title);
    });
  }

  it('shows several sources', () => {
    const translation = {
      sources: [...DEFAULT_TRANSLATION.sources, 'microsoft-terminology'],
    };
    const { getByText } = render(
      <WrapMachineryTranslationSource translation={translation} />,
    );

    getByText(translationMemoryTitle);
    getByText(microsoftTerminologyTitle);
  });
});
