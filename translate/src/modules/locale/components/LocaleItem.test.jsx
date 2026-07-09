import React from 'react';
import { render } from '@testing-library/react';
import LocaleItem from './LocaleItem';

function renderLocaleItem({ code = 'code', selected = false } = {}) {
  return render(
    <LocaleItem
      locale={{ code, name: 'Locale' }}
      currentLocale='current'
      selected={selected}
      onClick={() => {}}
    />,
  );
}

describe('<LocaleItem>', () => {
  it('renders correctly', () => {
    const { getByRole, getByText } = renderLocaleItem();
    getByRole('listitem');
    getByText('Locale');
    getByText('code');
  });

  it('sets the className when selected', () => {
    const { getByRole } = renderLocaleItem({ selected: true });
    expect(getByRole('listitem')).toHaveClass('selected');
  });

  it('does not set the selected className otherwise', () => {
    const { getByRole } = renderLocaleItem({ selected: false });
    expect(getByRole('listitem')).not.toHaveClass('selected');
  });
});
