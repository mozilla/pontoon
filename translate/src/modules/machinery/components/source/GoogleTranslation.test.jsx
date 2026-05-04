import React from 'react';

import { GoogleTranslation } from './GoogleTranslation';
import { fireEvent, render, within } from '@testing-library/react';
import { MockLocalizationProvider } from '~/test/utils';

vi.mock('~/hooks', () => ({
  useAppSelector: (selector) =>
    selector({
      term: { terms: [], fetching: false, sourceString: '' },
      teamcomments: { comments: [], fetching: false, entity: null },
    }),
}));

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

  it('renders the GoogleTranslation LLM features properly', () => {
    const mockTranslation = {
      translation: 'Translated text here',
      original: 'Original text here',
    };
    const message = 'test-source';

    const { container, getByRole } = render(
      <MockLocalizationProvider
        resources={[
          `machinery-GoogleTranslation--translation-source = ${message}`,
        ]}
      >
        <GoogleTranslation
          isOpenAIChatGPTSupported={true}
          translation={mockTranslation}
        />
      </MockLocalizationProvider>,
    );

    getByRole('listitem');

    expect(
      container.querySelector('span.translation-source'),
    ).toHaveTextContent(message);

    fireEvent.click(container.querySelector('.selector'));
    expect(within(getByRole('list')).getAllByRole('listitem')).toHaveLength(3);
  });
});
