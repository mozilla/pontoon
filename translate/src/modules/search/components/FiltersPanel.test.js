import React from 'react';
import { mount, shallow } from 'enzyme';
import sinon from 'sinon';

import FiltersPanelBase, { FiltersPanel } from './FiltersPanel';
import { FILTERS_STATUS, FILTERS_EXTRA } from '../constants';

describe('<FiltersPanel>', () => {
  it('correctly sets filter as selected', () => {
    const statuses = ['warnings', 'missing'];
    const extras = ['rejected'];

    const wrapper = mount(
      <FiltersPanel
        filters={{ authors: [], extras, statuses, tags: [] }}
        authorsData={[]}
        stats={{}}
        tagsData={[]}
        timeRangeData={[]}
      />,
    );

    for (let filter of FILTERS_STATUS) {
      expect(wrapper.find(`.menu .${filter.slug}`).hasClass('selected')).toBe(
        statuses.includes(filter.slug),
      );
    }

    for (let filter of FILTERS_EXTRA) {
      expect(wrapper.find(`.menu .${filter.slug}`).hasClass('selected')).toBe(
        extras.includes(filter.slug),
      );
    }
  });

  for (let { slug } of FILTERS_STATUS) {
    describe(`status: ${slug}`, () => {
      it('applies a single filter on click on a filter title', () => {
        const applySingleFilter = sinon.spy();
        const wrapper = mount(
          <FiltersPanel
            filters={{ authors: [], extras: [], statuses: [slug], tags: [] }}
            authorsData={[]}
            stats={{}}
            tagsData={[]}
            onApplyFilter={applySingleFilter}
            timeRangeData={[]}
          />,
        );
        wrapper.find(`.menu .${slug}`).simulate('click');

        expect(applySingleFilter.calledWith(slug)).toBeTruthy();
      });

      it('toggles a filter on click on a filter status icon', () => {
        const toggleFilter = sinon.spy();
        const wrapper = mount(
          <FiltersPanel
            filters={{ authors: [], extras: [], statuses: [slug], tags: [] }}
            authorsData={[]}
            parameters={{}}
            stats={{}}
            tagsData={[]}
            onToggleFilter={toggleFilter}
            timeRangeData={[]}
          />,
        );
        wrapper.find(`.menu .${slug} .status`).simulate('click');

        expect(toggleFilter.calledWith(slug)).toBeTruthy();
      });
    });
  }

  for (let { slug } of FILTERS_EXTRA) {
    describe(`extra: ${slug}`, () => {
      it('applies a single filter on click on a filter title', () => {
        const applySingleFilter = sinon.spy();
        const wrapper = mount(
          <FiltersPanel
            filters={{ authors: [], extras: [slug], statuses: [], tags: [] }}
            authorsData={[]}
            stats={{}}
            tagsData={[]}
            onApplyFilter={applySingleFilter}
            timeRangeData={[]}
          />,
        );
        wrapper.find(`.menu .${slug}`).simulate('click');

        expect(applySingleFilter.calledWith(slug)).toBeTruthy();
      });

      it('toggles a filter on click on a filter status icon', () => {
        const toggleFilter = sinon.spy();
        const wrapper = mount(
          <FiltersPanel
            filters={{ authors: [], extras: [slug], statuses: [], tags: [] }}
            authorsData={[]}
            parameters={{}}
            stats={{}}
            tagsData={[]}
            onToggleFilter={toggleFilter}
            timeRangeData={[]}
          />,
        );
        wrapper.find(`.menu .${slug} .status`).simulate('click');

        expect(toggleFilter.calledWith(slug)).toBeTruthy();
      });
    });
  }

  it('shows the toolbar when some filters are selected', () => {
    const wrapper = shallow(
      <FiltersPanel
        filters={{ authors: [], extras: [], statuses: [], tags: [] }}
        authorsData={[]}
        selectedFiltersCount={1}
        stats={{}}
        tagsData={[]}
      />,
    );

    expect(wrapper.find('FilterToolbar')).toHaveLength(1);
  });

  it('hides the toolbar when no filters are selected', () => {
    const wrapper = shallow(
      <FiltersPanel
        filters={{ authors: [], extras: [], statuses: [], tags: [] }}
        authorsData={[]}
        selectedFiltersCount={0}
        stats={{}}
        tagsData={[]}
      />,
    );

    expect(wrapper.find('FilterToolbar')).toHaveLength(0);
  });

  it('resets selected filters on click on the Clear button', () => {
    const resetFilters = sinon.spy();

    const wrapper = shallow(
      <FiltersPanel
        filters={{ authors: [], extras: [], statuses: [], tags: [] }}
        authorsData={[]}
        selectedFiltersCount={1}
        stats={{}}
        tagsData={[]}
        onResetFilters={resetFilters}
      />,
    );

    wrapper
      .find('FilterToolbar')
      .dive()
      .find('.clear-selection')
      .simulate('click');

    expect(resetFilters.called).toBeTruthy();
  });

  it('applies selected filters on click on the Apply button', () => {
    const update = sinon.spy();

    const wrapper = shallow(
      <FiltersPanel
        filters={{ authors: [], extras: [], statuses: [], tags: [] }}
        authorsData={[]}
        selectedFiltersCount={1}
        stats={{}}
        tagsData={[]}
        onApplyFilters={update}
      />,
    );

    wrapper
      .find('FilterToolbar')
      .dive()
      .find('.apply-selected')
      .simulate('click');

    expect(update.called).toBeTruthy();
  });
});

describe('<FiltersPanelBase>', () => {
  it('shows a panel with filters on click', () => {
    const wrapper = shallow(
      <FiltersPanelBase
        filters={{ authors: [], extras: [], statuses: [], tags: [] }}
        authorsData={[]}
        timeRangeData={[]}
        tagsData={[]}
        stats={{}}
        parameters={{}}
        getAuthorsAndTimeRangeData={sinon.spy()}
        updateFiltersFromURL={sinon.spy()}
      />,
    );

    expect(wrapper.find('FiltersPanel')).toHaveLength(0);
    wrapper.find('.visibility-switch').simulate('click');
    expect(wrapper.find('FiltersPanel')).toHaveLength(1);
  });

  it('has the correct icon based on parameters', () => {
    for (let { slug } of FILTERS_STATUS) {
      const wrapper = shallow(
        <FiltersPanelBase
          filters={{ authors: [], extras: [], statuses: [slug], tags: [] }}
          authorsData={[]}
          timeRangeData={[]}
          tagsData={[]}
          stats={{}}
          parameters={{}}
          getAuthorsAndTimeRangeData={sinon.spy()}
        />,
      );

      expect(wrapper.find('.visibility-switch').hasClass(slug)).toBeTruthy();
    }

    for (let { slug } of FILTERS_EXTRA) {
      const wrapper = shallow(
        <FiltersPanelBase
          filters={{ authors: [], extras: [slug], statuses: [], tags: [] }}
          authorsData={[]}
          timeRangeData={[]}
          tagsData={[]}
          stats={{}}
          parameters={{}}
          getAuthorsAndTimeRangeData={sinon.spy()}
        />,
      );

      expect(wrapper.find('.visibility-switch').hasClass(slug)).toBeTruthy();
    }
  });
});
