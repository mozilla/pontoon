import React from 'react';
import { expect } from 'vitest';

import { createReduxStore, mountComponentWithStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';
import { FiltersPanel, FiltersPanelDialog } from './FiltersPanel';
import { FILTERS_STATUS, FILTERS_EXTRA } from '../constants';
import { fireEvent, render, within } from '@testing-library/react';

describe('<FiltersPanelDialog>', () => {
  it('correctly sets filter as selected', () => {
    const statuses = ['warnings', 'missing'];
    const extras = ['rejected'];

    const store = createReduxStore();
    const { container } = mountComponentWithStore(FiltersPanelDialog, store, {
      filters: { authors: [], extras, statuses, tags: [] },
      authorsData: [],
      tagsData: [],
      timeRangeData: [],
    });

    for (const filter of FILTERS_STATUS) {
      expect(
        container
          .querySelector(`.menu .${filter.slug}`)
          .classList.contains('selected'),
      ).toBe(statuses.includes(filter.slug));
    }

    for (const filter of FILTERS_EXTRA) {
      expect(
        container
          .querySelector(`.menu .${filter.slug}`)
          .classList.contains('selected'),
      ).toBe(extras.includes(filter.slug));
    }
  });

  for (const { slug, name } of FILTERS_STATUS) {
    describe(`status: ${slug}`, () => {
      it('applies a single filter on click on a filter title', () => {
        const onApplyFilter = vi.fn();
        const store = createReduxStore();
        const { getByText } = mountComponentWithStore(
          FiltersPanelDialog,
          store,
          {
            filters: { authors: [], extras: [], statuses: [slug], tags: [] },
            onApplyFilter,
            authorsData: [],
            tagsData: [],
            timeRangeData: [],
          },
        );

        fireEvent.click(getByText(name));

        expect(onApplyFilter).toHaveBeenCalledWith(slug, expect.anything());
      });

      it('toggles a filter on click on a filter status icon', () => {
        const onToggleFilter = vi.fn();
        const store = createReduxStore();
        const { container } = mountComponentWithStore(
          FiltersPanelDialog,
          store,
          {
            filters: { authors: [], extras: [], statuses: [slug], tags: [] },
            onToggleFilter,
            parameters: {},
            authorsData: [],
            tagsData: [],
            timeRangeData: [],
          },
        );

        fireEvent.click(container.querySelector(`.menu .${slug} .status`));

        expect(onToggleFilter).toHaveBeenCalledWith(slug, expect.anything());
      });
    });
  }

  for (const { slug, name } of FILTERS_EXTRA) {
    describe(`extra: ${slug}`, () => {
      it('applies a single filter on click on a filter title', () => {
        const onApplyFilter = vi.fn();
        const store = createReduxStore();
        const { getByText } = mountComponentWithStore(
          FiltersPanelDialog,
          store,
          {
            filters: { authors: [], extras: [slug], statuses: [], tags: [] },
            onApplyFilter,
            authorsData: [],
            tagsData: [],
            timeRangeData: [],
          },
        );

        fireEvent.click(getByText(name));

        expect(onApplyFilter).toHaveBeenCalledWith(slug, expect.anything());
      });

      it('toggles a filter on click on a filter status icon', () => {
        const onToggleFilter = vi.fn();
        const store = createReduxStore();
        const { container } = mountComponentWithStore(
          FiltersPanelDialog,
          store,
          {
            filters: { authors: [], extras: [slug], statuses: [], tags: [] },
            onToggleFilter,
            parameters: {},
            authorsData: [],
            tagsData: [],
            timeRangeData: [],
          },
        );

        fireEvent.click(container.querySelector(`.menu .${slug} .status`));

        expect(onToggleFilter).toHaveBeenCalledWith(slug, expect.anything());
      });
    });
  }

  it('shows the toolbar when some filters are selected', () => {
    const store = createReduxStore();
    const { getByRole } = mountComponentWithStore(FiltersPanelDialog, store, {
      filters: { authors: [], extras: [], statuses: [], tags: [] },
      selectedFiltersCount: 1,
      authorsData: [],
      tagsData: [],
      timeRangeData: [],
    });

    getByRole('button', { name: /clear/i });
    getByRole('button', { name: /apply/i });
  });

  it('hides the toolbar when no filters are selected', () => {
    const store = createReduxStore();
    const { queryByRole } = mountComponentWithStore(FiltersPanelDialog, store, {
      filters: { authors: [], extras: [], statuses: [], tags: [] },
      selectedFiltersCount: 0,
      authorsData: [],
      tagsData: [],
      timeRangeData: [],
    });

    expect(queryByRole('button', { name: /clear/i })).not.toBeInTheDocument();
    expect(queryByRole('button', { name: /apply/i })).not.toBeInTheDocument();
  });

  it('resets selected filters on click on the Clear button', () => {
    const onResetFilters = vi.fn();
    const store = createReduxStore();
    const { getByRole } = mountComponentWithStore(FiltersPanelDialog, store, {
      filters: { authors: [], extras: [], statuses: [], tags: [] },
      onResetFilters,
      selectedFiltersCount: 1,
      authorsData: [],
      tagsData: [],
      timeRangeData: [],
    });

    fireEvent.click(getByRole('button', { name: /clear/i }));

    expect(onResetFilters).toHaveBeenCalled();
  });

  it('applies selected filters on click on the Apply button', () => {
    const onApplyFilters = vi.fn();
    const store = createReduxStore();
    const { getByRole } = mountComponentWithStore(FiltersPanelDialog, store, {
      filters: { authors: [], extras: [], statuses: [], tags: [] },
      onApplyFilters,
      selectedFiltersCount: 1,
      authorsData: [],
      tagsData: [],
      timeRangeData: [],
    });

    fireEvent.click(getByRole('button', { name: /apply/i }));

    expect(onApplyFilters).toHaveBeenCalled();
  });
});

describe('<FiltersPanel>', () => {
  const FilterPanelDialogTitle = 'TRANSLATION STATUS';
  it('shows a panel with filters on click', () => {
    const store = createReduxStore();
    const { getByText, queryByText, getByRole } = mountComponentWithStore(
      FiltersPanel,
      store,
      {
        filters: { authors: [], extras: [], statuses: [], tags: [] },
        authorsData: [],
        tagsData: [],
        timeRangeData: [],
        parameters: {},
        getAuthorsAndTimeRangeData: vi.fn(),
        updateFiltersFromURL: vi.fn(),
      },
    );

    expect(queryByText(FilterPanelDialogTitle)).toBeNull();
    fireEvent.click(getByRole('button'));
    getByText(FilterPanelDialogTitle);
  });

  it('has the correct icon based on parameters', () => {
    const toggleAriaLabel = 'Toggle';
    for (const { slug } of FILTERS_STATUS) {
      const { container } = mountComponentWithStore(
        FiltersPanel,
        createReduxStore(),
        {
          filters: { authors: [], extras: [], statuses: [slug], tags: [] },
          authorsData: [],
          tagsData: [],
          timeRangeData: [],
          parameters: {},
          getAuthorsAndTimeRangeData: vi.fn(),
        },
        undefined,
        [
          `search-FiltersPanel--toggle-filters-panel =
            .aria-label = ${toggleAriaLabel}`
        ],
      );

      const button = within(container).getByRole('button', { name: toggleAriaLabel });
      expect(button).toHaveClass('visibility-switch');
      expect(button).toHaveClass(slug);
    }

    for (const { slug } of FILTERS_EXTRA) {
      const { container } = mountComponentWithStore(
        FiltersPanel,
        createReduxStore(),
        {
          filters: { authors: [], extras: [slug], statuses: [], tags: [] },
          authorsData: [],
          tagsData: [],
          timeRangeData: [],
          parameters: {},
          getAuthorsAndTimeRangeData: vi.fn(),
        },
        undefined,
        [
          `search-FiltersPanel--toggle-filters-panel =
            .aria-label = ${toggleAriaLabel}`
        ],
      );
 
      const button = within(container).getByRole('button', { name: toggleAriaLabel });
      expect(button).toHaveClass('visibility-switch');
      expect(button).toHaveClass(slug);
    }
  });
});
