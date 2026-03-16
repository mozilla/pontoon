import React from 'react';

import { CaighdeanTranslation } from './CaighdeanTranslation';
import { render } from '@testing-library/react';
import { MockLocalizationProvider } from '~/test/utils';

describe('<CaighdeanTranslation>', () => {
  it('renders the CaighdeanTranslation component properly', () => {
    const message = 'test-caighdean-translation';
    const { getByRole, getByText } = render(
      <MockLocalizationProvider
        resources={[
          `machinery-CaighdeanTranslation--translation-source = ${message}`,
        ]}
      >
        <CaighdeanTranslation />
      </MockLocalizationProvider>,
    );

    getByRole('listitem');
    getByText(message);
  });
});
