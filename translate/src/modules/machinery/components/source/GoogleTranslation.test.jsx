import React from 'react';

import { GoogleTranslation } from './GoogleTranslation';
import { render } from '@testing-library/react';
import { MockLocalizationProvider } from '~/test/utils';

describe('<GoogleTranslation>', () => {
  it('renders the GoogleTranslation component properly', () => {
    const message = 'test-source';
    const { getByRole, getByText } = render(
      <MockLocalizationProvider
        resources={[
          `machinery-GoogleTranslation--translation-source = ${message}`,
        ]}
      >
        <GoogleTranslation />
      </MockLocalizationProvider>,
    );

    getByRole('listitem');
    getByText(message);
  });
});
