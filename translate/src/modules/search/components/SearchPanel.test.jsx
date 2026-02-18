import React from 'react';

import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { SearchPanel, SearchPanelDialog } from './SearchPanel';
import { SEARCH_OPTIONS } from '../constants';
import { fireEvent, render } from '@testing-library/react';
import { expect } from 'vitest';

const selectedSearchOptions = {
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
      options: selectedSearchOptions,
      selectedSearchOptions,
    });

    for (const { slug } of SEARCH_OPTIONS) {
      expect(
        container.querySelector(`.menu .${slug}`).classList.contains('enabled'),
      ).toBe(selectedSearchOptions[slug]);
    }
  });

  for (const { slug, name } of SEARCH_OPTIONS) {
    describe(`option: ${slug}`, () => {
      it('toggles a search option on click on the option icon', () => {
        const onToggleOption = vi.fn();
        const store = createReduxStore();

        const { getByText } = mountComponentWithStore(
          SearchPanelDialog,
          store,
          {
            selectedSearchOptions: selectedSearchOptions,
            onApplyOptions: vi.fn(),
            onToggleOption,
            onDiscard: vi.fn(),
          },
        );

        fireEvent.click(getByText(name));

        expect(onToggleOption).toHaveBeenCalledWith(slug);
      });
    });
  }

  it('applies selected options on click on the Apply button', () => {
    const onApplyOptions = vi.fn();
    const store = createReduxStore();
    const { getByRole } = mountComponentWithStore(SearchPanelDialog, store, {
      selectedSearchOptions: selectedSearchOptions,
      onApplyOptions,
    });

    fireEvent.click(getByRole('button', { name: 'APPLY SEARCH OPTIONS' }));

    expect(onApplyOptions).toHaveBeenCalled();
  });
});

describe('<SearchPanel>', () => {
  it('shows a panel with options on click', () => {
    const { queryByRole, getByRole } = render(
      <SearchPanel searchOptions={selectedSearchOptions} />,
    );

    expect(queryByRole('banner')).not.toBeInTheDocument();
    fireEvent.click(getByRole('button'));
    expect(getByRole('banner')).toHaveTextContent('SEARCH OPTIONS');
  });
});
