import React from 'react';

import { Locale } from '~/context/Locale';

import { MockLocalizationProvider } from '~/test/utils';

import { MicrosoftTerminology } from './MicrosoftTerminology';
import { render } from '@testing-library/react';

const LOCALE = { msTerminologyCode: 'en-US' };
const PROPS = {
  original: 'A horse, a horse! My kingdom for a horse',
};

describe('<MicrosoftTerminology>', () => {
  it('renders the MicrosoftTerminology component properly', () => {
    const message = 'test-message';
    const { getByRole } = render(
      <Locale.Provider value={LOCALE}>
        <MockLocalizationProvider
          resources={[
            `machinery-MicrosoftTerminology--translation-source = ${message}`,
          ]}
        >
          <MicrosoftTerminology original={PROPS.original} />
        </MockLocalizationProvider>
      </Locale.Provider>,
    );

    expect(
      getByRole('listitem').querySelector('span.translation-source'),
    ).toHaveTextContent(message);
  });
});
