import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { FiltersPanel, FiltersPanelDialog } from './FiltersPanel';
import { FILTERS_STATUS, FILTERS_EXTRA } from '../constants';

describe('<FiltersPanelDialog>', () => {
  it('correctly sets filter as selected', () => {
    const statuses = ['warnings', 'missing'];
    const extras = ['rejected'];

    const store = createReduxStore();
    const wrapper = mountComponentWithStore(FiltersPanelDialog, store, {
      filters: { authors: [], extras, statuses, tags: [] },
      authorsData: [],
      tagsData: [],
      timeRangeData: [],
    });

    for (const filter of FILTERS_STATUS) {
      expect(wrapper.find(`.menu .${filter.slug}`).hasClass('selected')).toBe(
        statuses.includes(filter.slug),
      );
    }

    for (const filter of FILTERS_EXTRA) {
      expect(wrapper.find(`.menu .${filter.slug}`).hasClass('selected')).toBe(
        extras.includes(filter.slug),
      );
    }
  });

  for (const { slug } of FILTERS_STATUS) {
    describe(`status: ${slug}`, () => {
      it('applies a single filter on click on a filter title', () => {
        const onApplyFilter = sinon.spy();
        const store = createReduxStore();
        const wrapper = mountComponentWithStore(FiltersPanelDialog, store, {
          filters: { authors: [], extras: [], statuses: [slug], tags: [] },
          onApplyFilter,
          authorsData: [],
          tagsData: [],
          timeRangeData: [],
        });

        wrapper.find(`.menu .${slug}`).simulate('click');

        expect(onApplyFilter.calledWith(slug)).toBeTruthy();
      });

      it('toggles a filter on click on a filter status icon', () => {
        const onToggleFilter = sinon.spy();
        const store = createReduxStore();
        const wrapper = mountComponentWithStore(FiltersPanelDialog, store, {
          filters: { authors: [], extras: [], statuses: [slug], tags: [] },
          onToggleFilter,
          parameters: {},
          authorsData: [],
          tagsData: [],
          timeRangeData: [],
        });

        wrapper.find(`.menu .${slug} .status`).simulate('click');

        expect(onToggleFilter.calledWith(slug)).toBeTruthy();
      });
    });
  }

  for (const { slug } of FILTERS_EXTRA) {
    describe(`extra: ${slug}`, () => {
      it('applies a single filter on click on a filter title', () => {
        const onApplyFilter = sinon.spy();
        const store = createReduxStore();
        const wrapper = mountComponentWithStore(FiltersPanelDialog, store, {
          filters: { authors: [], extras: [slug], statuses: [], tags: [] },
          onApplyFilter,
          authorsData: [],
          tagsData: [],
          timeRangeData: [],
        });

        wrapper.find(`.menu .${slug}`).simulate('click');

        expect(onApplyFilter.calledWith(slug)).toBeTruthy();
      });

      it('toggles a filter on click on a filter status icon', () => {
        const onToggleFilter = sinon.spy();
        const store = createReduxStore();
        const wrapper = mountComponentWithStore(FiltersPanelDialog, store, {
          filters: { authors: [], extras: [slug], statuses: [], tags: [] },
          onToggleFilter,
          parameters: {},
          authorsData: [],
          tagsData: [],
          timeRangeData: [],
        });

        wrapper.find(`.menu .${slug} .status`).simulate('click');

        expect(onToggleFilter.calledWith(slug)).toBeTruthy();
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

    expect(wrapper.find('FilterToolbar')).toHaveLength(1);
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

    expect(wrapper.find('FilterToolbar')).toHaveLength(0);
  });

  it('resets selected filters on click on the Clear button', () => {
    const onResetFilters = sinon.spy();
    const store = createReduxStore();
    const wrapper = mountComponentWithStore(FiltersPanelDialog, store, {
      filters: { authors: [], extras: [], statuses: [], tags: [] },
      onResetFilters,
      selectedFiltersCount: 1,
      authorsData: [],
      tagsData: [],
      timeRangeData: [],
    });

    wrapper.find('FilterToolbar .clear-selection').simulate('click');

    expect(onResetFilters.called).toBeTruthy();
  });

  it('applies selected filters on click on the Apply button', () => {
    const onApplyFilters = sinon.spy();
    const store = createReduxStore();
    const wrapper = mountComponentWithStore(FiltersPanelDialog, store, {
      filters: { authors: [], extras: [], statuses: [], tags: [] },
      onApplyFilters,
      selectedFiltersCount: 1,
      authorsData: [],
      tagsData: [],
      timeRangeData: [],
    });

    wrapper.find('FilterToolbar .apply-selected').simulate('click');

    expect(onApplyFilters.called).toBeTruthy();
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
        getAuthorsAndTimeRangeData={sinon.spy()}
        updateFiltersFromURL={sinon.spy()}
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
          getAuthorsAndTimeRangeData={sinon.spy()}
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
          getAuthorsAndTimeRangeData={sinon.spy()}
        />,
      );

      expect(wrapper.find('.visibility-switch').hasClass(slug)).toBeTruthy();
    }
  });
});
