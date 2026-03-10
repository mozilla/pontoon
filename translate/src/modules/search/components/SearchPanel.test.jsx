import React from 'react';

import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { SearchPanel, SearchPanelDialog } from './SearchPanel';
import { SEARCH_OPTIONS } from '../constants';
import { fireEvent, render } from '@testing-library/react';
import { expect } from 'vitest';

const searchOptions = {
  search_identifiers: false,
  search_exclude_source_strings: false,
  search_rejected_translations: true,
  search_match_case: true,
  search_match_whole_word: false,
};

vi.mock('@fluent/react', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    Localized: ({ children }) => children,
  };
});

describe('<SearchPanelDialog>', () => {
  it('correctly sets search option as selected', () => {
    const store = createReduxStore();
    const { container } = mountComponentWithStore(SearchPanelDialog, store, {
      searchOptions,
      onApplyOptions: vi.fn(),
      onToggleOption: vi.fn(),
      onRestoreDefaults: vi.fn(),
      onDiscard: vi.fn(),
    });

    for (const { slug } of SEARCH_OPTIONS) {
      expect(
        container.querySelector(`.menu .${slug}`).classList.contains('enabled'),
      ).toBe(searchOptions[slug]);
    }
  });

  for (const { slug, name } of SEARCH_OPTIONS) {
    describe(`option: ${slug}`, () => {
      it('toggles a search option on click', () => {
        const onToggleOption = vi.fn();
        const store = createReduxStore();

        const { getByText } = mountComponentWithStore(
          SearchPanelDialog,
          store,
          {
            searchOptions,
            onApplyOptions: vi.fn(),
            onToggleOption,
            onRestoreDefaults: vi.fn(),
            onDiscard: vi.fn(),
          },
        );

        fireEvent.click(getByText(name));

        expect(onToggleOption).toHaveBeenCalledWith(slug);
      });
    });
  }

  it('calls onRestoreDefaults on click on Restore default options', () => {
    const onRestoreDefaults = vi.fn();
    const store = createReduxStore();
    const { getByText } = mountComponentWithStore(SearchPanelDialog, store, {
      searchOptions,
      onApplyOptions: vi.fn(),
      onToggleOption: vi.fn(),
      onRestoreDefaults,
      onDiscard: vi.fn(),
    });

    fireEvent.click(getByText('Restore default options'));

    expect(onRestoreDefaults).toHaveBeenCalled();
  });

  it('calls onApplyOptions on click on Apply search options', () => {
    const onApplyOptions = vi.fn();
    const store = createReduxStore();
    const { getByText } = mountComponentWithStore(SearchPanelDialog, store, {
      searchOptions,
      onApplyOptions,
      onToggleOption: vi.fn(),
      onRestoreDefaults: vi.fn(),
      onDiscard: vi.fn(),
    });

    fireEvent.click(getByText('APPLY SEARCH OPTIONS'));

    expect(onApplyOptions).toHaveBeenCalled();
  });
});

describe('<SearchPanel>', () => {
  it('shows a panel with options on click', () => {
    const { queryByRole, getByRole } = render(
      <SearchPanel
        searchOptions={searchOptions}
        applyOptions={vi.fn()}
        restoreDefaults={vi.fn()}
        toggleOption={vi.fn()}
      />,
    );

    expect(queryByRole('banner')).not.toBeInTheDocument();
    fireEvent.click(getByRole('button'));
    expect(getByRole('banner')).toHaveTextContent('SEARCH OPTIONS');
  });

  it('keeps the panel open after toggling an option', () => {
    const { getByRole, getByText } = render(
      <SearchPanel
        searchOptions={searchOptions}
        applyOptions={vi.fn()}
        restoreDefaults={vi.fn()}
        toggleOption={vi.fn()}
      />,
    );

    fireEvent.click(getByRole('button'));
    expect(getByRole('banner')).toBeInTheDocument();

    fireEvent.click(getByText('Match case'));
    expect(getByRole('banner')).toBeInTheDocument();
  });

  it('hides the panel after clicking Apply search options', () => {
    const { queryByRole, getByRole, getByText } = render(
      <SearchPanel
        searchOptions={searchOptions}
        applyOptions={vi.fn()}
        restoreDefaults={vi.fn()}
        toggleOption={vi.fn()}
      />,
    );

    fireEvent.click(getByRole('button'));
    expect(getByRole('banner')).toBeInTheDocument();

    fireEvent.click(getByText('APPLY SEARCH OPTIONS'));
    expect(queryByRole('banner')).not.toBeInTheDocument();
  });
});
