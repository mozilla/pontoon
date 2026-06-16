import React from 'react';
import { ResourcePercent } from './ResourcePercent';
import { render } from '@testing-library/react';

describe('<ResourcePercent>', () => {
  const RESOURCE = {
    approvedStrings: 2,
    pretranslatedStrings: 1,
    stringsWithWarnings: 2,
    totalStrings: 10,
  };

  it('renders correctly', () => {
    const { getByText } = render(<ResourcePercent resource={RESOURCE} />);
    getByText('40%');
  });
});
