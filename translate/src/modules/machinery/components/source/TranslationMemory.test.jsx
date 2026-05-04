import React from 'react';

import { TranslationMemory } from './TranslationMemory';
import { render } from '@testing-library/react';
import { expect } from 'vitest';
import { MockLocalizationProvider } from '~/test/utils';

describe('<TranslationMemory>', () => {
  it('renders the component without number of occurrences properly', () => {
    const title = 'test-title';
    const { getByRole } = render(
      <MockLocalizationProvider
        resources={[
          `machinery-TranslationMemory--translation-source = ${title}`,
        ]}
      >
        <TranslationMemory />
      </MockLocalizationProvider>,
    );

    getByRole('listitem');
    expect(
      getByRole('listitem').querySelector('span.translation-source'),
    ).toHaveTextContent(title);
  });

  it('renders the component with number of occurrences properly', () => {
    const occurrenceMsg = 'test-occurrence';
    const title = 'test-title';
    const { getByRole, getByText, container, getByTitle } = render(
      <MockLocalizationProvider
        resources={[
          `machinery-TranslationMemory--number-occurrences = 
                    .title = ${occurrenceMsg}`,
          `machinery-TranslationMemory--translation-source = ${title}`,
        ]}
      >
        <TranslationMemory itemCount={2} />
      </MockLocalizationProvider>,
    );

    getByRole('listitem');
    getByText(title);

    expect(container.querySelector('sup')).toHaveTextContent('2');
    getByTitle(occurrenceMsg);
  });
});
