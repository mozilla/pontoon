import React from 'react';
import { shallow } from 'enzyme';
import { expect } from 'vitest';

import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { FiltersPanel, FiltersPanelDialog } from './FiltersPanel';
import { FILTERS_STATUS, FILTERS_EXTRA } from '../constants';
import { fireEvent } from '@testing-library/react';

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

  for (const { slug } of FILTERS_STATUS) {
    describe(`status: ${slug}`, () => {
      it('applies a single filter on click on a filter title', () => {
        const onApplyFilter = vi.fn();
        const store = createReduxStore();
        const { container } = mountComponentWithStore(
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

        fireEvent.click(container.querySelector(`.menu .${slug}`));

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

  for (const { slug } of FILTERS_EXTRA) {
    describe(`extra: ${slug}`, () => {
      it('applies a single filter on click on a filter title', () => {
        const onApplyFilter = vi.fn();
        const store = createReduxStore();
        const { container } = mountComponentWithStore(
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

        fireEvent.click(container.querySelector(`.menu .${slug}`));

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
    const wrapper = mountComponentWithStore(FiltersPanelDialog, store, {
      filters: { authors: [], extras: [], statuses: [], tags: [] },
      selectedFiltersCount: 1,
      authorsData: [],
      tagsData: [],
      timeRangeData: [],
    });

    expect(wrapper.queryByTestId('filter-toolbar')).toBeInTheDocument();
  });

  it('hides the toolbar when no filters are selected', () => {
    const store = createReduxStore();
    const wrapper = mountComponentWithStore(FiltersPanelDialog, store, {
      filters: { authors: [], extras: [], statuses: [], tags: [] },
      selectedFiltersCount: 0,
      authorsData: [],
      tagsData: [],
      timeRangeData: [],
    });

    expect(wrapper.queryByTestId('filter-toolbar')).not.toBeInTheDocument();
  });

  it('resets selected filters on click on the Clear button', () => {
    const onResetFilters = vi.fn();
    const store = createReduxStore();
    const wrapper = mountComponentWithStore(FiltersPanelDialog, store, {
      filters: { authors: [], extras: [], statuses: [], tags: [] },
      onResetFilters,
      selectedFiltersCount: 1,
      authorsData: [],
      tagsData: [],
      timeRangeData: [],
    });

    fireEvent.click(
      wrapper.queryByTestId('filter-toolbar').querySelector('.clear-selection'),
    );

    expect(onResetFilters).toHaveBeenCalled();
  });

  it('applies selected filters on click on the Apply button', () => {
    const onApplyFilters = vi.fn();
    const store = createReduxStore();
    const wrapper = mountComponentWithStore(FiltersPanelDialog, store, {
      filters: { authors: [], extras: [], statuses: [], tags: [] },
      onApplyFilters,
      selectedFiltersCount: 1,
      authorsData: [],
      tagsData: [],
      timeRangeData: [],
    });

    fireEvent.click(
      wrapper.queryByTestId('filter-toolbar').querySelector('.apply-selected'),
    );

    expect(onApplyFilters).toHaveBeenCalled();
  });
});

describe('<FiltersPanel>', () => {
  it('shows a panel with filters on click', () => {
    const wrapper = shallow(
      <FiltersPanel
        filters={{ authors: [], extras: [], statuses: [], tags: [] }}
        authorsData={[]}
        tagsData={[]}
        timeRangeData={[]}
        parameters={{}}
        getAuthorsAndTimeRangeData={vi.fn()}
        updateFiltersFromURL={vi.fn()}
      />,
    );

    expect(wrapper.find('FiltersPanelDialog')).toHaveLength(0);
    wrapper.find('.visibility-switch').simulate('click');
    expect(wrapper.find('FiltersPanelDialog')).toHaveLength(1);
  });

  it('has the correct icon based on parameters', () => {
    for (const { slug } of FILTERS_STATUS) {
      const wrapper = shallow(
        <FiltersPanel
          filters={{ authors: [], extras: [], statuses: [slug], tags: [] }}
          authorsData={[]}
          tagsData={[]}
          timeRangeData={[]}
          parameters={{}}
          getAuthorsAndTimeRangeData={vi.fn()}
        />,
      );

      expect(wrapper.find('.visibility-switch').hasClass(slug)).toBeTruthy();
    }

    for (const { slug } of FILTERS_EXTRA) {
      const wrapper = shallow(
        <FiltersPanel
          filters={{ authors: [], extras: [slug], statuses: [], tags: [] }}
          authorsData={[]}
          tagsData={[]}
          timeRangeData={[]}
          parameters={{}}
          getAuthorsAndTimeRangeData={vi.fn()}
        />,
      );

      expect(wrapper.find('.visibility-switch').hasClass(slug)).toBeTruthy();
    }
  });
});
