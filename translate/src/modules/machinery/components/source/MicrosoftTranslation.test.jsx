import React from 'react';

import { MicrosoftTranslation } from './MicrosoftTranslation';
import { render } from '@testing-library/react';
import { MockLocalizationProvider } from '~/test/utils';

describe('<MicrosoftTranslation>', () => {
  it('renders the MicrosoftTranslation component properly', () => {
    const message = 'test-message';
    const { getByRole } = render(
      <MockLocalizationProvider
        resources={[
          `machinery-MicrosoftTranslation--translation-source = ${message}`,
        ]}
      >
        <MicrosoftTranslation />
      </MockLocalizationProvider>,
    );

    expect(
      getByRole('listitem').querySelector('span.translation-source'),
    ).toHaveTextContent(message);
  });
});
