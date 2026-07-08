import React from 'react';

import { LocaleItem } from './LocaleItem';
import { render } from '@testing-library/react';

function renderLocaleItem({ code = 'code' } = {}) {
  return render(
    <LocaleItem
      locale={{ code, name: 'Locale' }}
      currentLocale='current'
      selected={code === 'current'}
      onClick={() => {}}
    />,
  );
}

describe('<LocaleItem>', () => {
  it('renders correctly', () => {
    const { getByRole, container } = renderLocaleItem();
    getByRole('listitem');
    expect(container.querySelector('span.locale')).toBeInTheDocument();
  });

  it('sets the className for the current locale', () => {
    const { getByRole } = renderLocaleItem({ code: 'current' });
    expect(getByRole('listitem')).toHaveClass('current');
  });

  it('sets the className for another locale', () => {
    const { getByRole } = renderLocaleItem();
    expect(getByRole('listitem')).not.toHaveClass('current');
  });
});
