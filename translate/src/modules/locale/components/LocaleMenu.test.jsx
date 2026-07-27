import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import LocaleMenu from './LocaleMenu';

function renderLocaleMenu({
  currentLocale = 'current',
  selected = '',
  onSelect = () => {},
} = {}) {
  return render(
    <LocaleMenu
      locales={[
        { code: 'code1', name: 'Locale 1' },
        { code: 'code2', name: 'Locale 2' },
        { code: 'current', name: 'Current Locale' },
      ]}
      currentLocale={currentLocale}
      selected={selected}
      onSelect={onSelect}
    />,
  );
}

describe('<LocaleMenu>', () => {
  it('renders correctly', () => {
    const { getByRole } = renderLocaleMenu();
    getByRole('button');
  });

  it('opens the menu when the button is clicked', () => {
    const { getByRole, getByText, queryByText, container } = renderLocaleMenu();
    const button = getByRole('button');
    fireEvent.click(button);

    expect(container.querySelector('input')).toBeInTheDocument();
    getByText('Locale 1');
    getByText('Locale 2');
    expect(queryByText('Current Locale')).toBeNull();
  });

  it('filters the locales based on the search input', () => {
    const { getByRole, getByText, queryByText } = renderLocaleMenu();
    const button = getByRole('button');
    fireEvent.click(button);

    const input = getByRole('searchbox');
    fireEvent.change(input, { target: { value: 'Locale 1' } });

    getByText('Locale 1');
    expect(queryByText('Locale 2')).toBeNull();
  });

  it('calls onSelect and closes the menu when a locale is clicked', () => {
    const onSelect = vi.fn();
    const { getByRole, getByText, queryByText } = renderLocaleMenu({
      onSelect,
    });
    fireEvent.click(getByRole('button'));

    fireEvent.click(getByText('Locale 1'));

    expect(onSelect).toHaveBeenCalledWith('code1');
    expect(queryByText('Locale 1')).toBeNull();
  });
});
