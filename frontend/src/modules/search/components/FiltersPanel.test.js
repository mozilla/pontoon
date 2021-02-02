import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import FiltersPanelBase, { FiltersPanel } from './FiltersPanel';
import { FILTERS_STATUS, FILTERS_EXTRA } from '../constants';

const FILTERS = [].concat(FILTERS_STATUS, FILTERS_EXTRA);

describe('<FiltersPanel>', () => {
    it('correctly sets filter as selected', () => {
        const statuses = {
            warnings: true,
            errors: false,
            missing: true,
        };

        const extras = {
            unchanged: false,
            rejected: true,
        };

        const wrapper = shallow(
            <FiltersPanel
                authorsData={[]}
                extras={extras}
                stats={{}}
                statuses={statuses}
                tagsData={[]}
            />,
        );

        for (let filter of FILTERS) {
            let isFilterSelected;

            if (FILTERS_STATUS.includes(filter)) {
                isFilterSelected = statuses[filter.slug];
            } else if (FILTERS_EXTRA.includes(filter)) {
                isFilterSelected = extras[filter.slug];
            }

            const isClassSet = wrapper
                .find(`.menu .${filter.slug}`)
                .hasClass('selected');

            if (isFilterSelected) {
                expect(isClassSet).toBeTruthy();
            } else {
                expect(isClassSet).toBeFalsy();
            }
        }
    });

    it('applies a single filter on click on a filter title', () => {
        let applySingleFilter;

        for (let filter of FILTERS) {
            let statuses = {};
            let extras = {};

            const value = {
                [filter.slug]: true,
            };

            if (FILTERS_STATUS.includes(filter)) {
                statuses = value;
            } else if (FILTERS_EXTRA.includes(filter)) {
                extras = value;
            }

            applySingleFilter = sinon.spy();

            const wrapper = shallow(
                <FiltersPanel
                    authorsData={[]}
                    extras={extras}
                    stats={{}}
                    statuses={statuses}
                    tagsData={[]}
                    onApplyFilter={applySingleFilter}
                />,
            );
            wrapper.find(`.menu .${filter.slug}`).simulate('click');

            expect(applySingleFilter.calledWith(filter.slug)).toBeTruthy();
        }
    });

    it('toggles a filter on click on a filter status icon', () => {
        let toggleFilter;

        for (let filter of FILTERS) {
            let statuses = {};
            let extras = {};

            const value = {
                [filter.slug]: false,
            };

            if (FILTERS_STATUS.includes(filter)) {
                statuses = value;
            } else if (FILTERS_EXTRA.includes(filter)) {
                extras = value;
            }

            toggleFilter = sinon.spy();
            const wrapper = shallow(
                <FiltersPanel
                    authorsData={[]}
                    extras={extras}
                    parameters={{}}
                    stats={{}}
                    statuses={statuses}
                    tagsData={[]}
                    onToggleFilter={toggleFilter}
                />,
            );
            wrapper.find(`.menu .${filter.slug} .status`).simulate('click');

            expect(toggleFilter.calledWith(filter.slug)).toBeTruthy();
        }
    });

    it('shows the toolbar when some filters are selected', () => {
        const wrapper = shallow(
            <FiltersPanel
                authorsData={[]}
                extras={{}}
                selectedFiltersCount={1}
                stats={{}}
                statuses={{}}
                tagsData={[]}
            />,
        );

        expect(wrapper.find('.toolbar')).toHaveLength(1);
    });

    it('hides the toolbar when no filters are selected', () => {
        const wrapper = shallow(
            <FiltersPanel
                authorsData={[]}
                extras={{}}
                selectedFiltersCount={0}
                stats={{}}
                statuses={{}}
                tagsData={[]}
            />,
        );

        expect(wrapper.find('.toolbar')).toHaveLength(0);
    });

    it('resets selected filters on click on the Clear button', () => {
        const resetFilters = sinon.spy();

        const wrapper = shallow(
            <FiltersPanel
                authorsData={[]}
                extras={{}}
                selectedFiltersCount={1}
                stats={{}}
                statuses={{}}
                tagsData={[]}
                onResetFilters={resetFilters}
            />,
        );

        wrapper.find('.toolbar .clear-selection').simulate('click');

        expect(resetFilters.called).toBeTruthy();
    });

    it('applies selected filters on click on the Apply button', () => {
        const update = sinon.spy();

        const wrapper = shallow(
            <FiltersPanel
                authorsData={[]}
                extras={{}}
                selectedFiltersCount={1}
                stats={{}}
                statuses={{}}
                tagsData={[]}
                onApplyFilters={update}
            />,
        );

        wrapper.find('.toolbar .apply-selected').simulate('click');

        expect(update.called).toBeTruthy();
    });
});

describe('<FiltersPanelBase>', () => {
    it('shows a panel with filters on click', () => {
        const statuses = {};
        const extras = {};

        const wrapper = shallow(
            <FiltersPanelBase
                statuses={statuses}
                extras={extras}
                tags={{}}
                authors={{}}
                authorsData={[]}
                timeRangeData={[]}
                tagsData={[]}
                stats={{}}
                parameters={{}}
                getAuthorsAndTimeRangeData={sinon.spy()}
                updateFiltersFromURLParams={sinon.spy()}
            />,
        );

        expect(wrapper.find('FiltersPanel')).toHaveLength(0);
        wrapper.find('.visibility-switch').simulate('click');
        expect(wrapper.find('FiltersPanel')).toHaveLength(1);
    });

    it('has the correct icon based on parameters', () => {
        for (let filter of FILTERS) {
            let statuses = {};
            let extras = {};

            const value = {
                [filter.slug]: true,
            };

            if (FILTERS_STATUS.includes(filter)) {
                statuses = value;
            } else if (FILTERS_EXTRA.includes(filter)) {
                extras = value;
            }

            const wrapper = shallow(
                <FiltersPanelBase
                    statuses={statuses}
                    extras={extras}
                    tags={{}}
                    authors={{}}
                    authorsData={[]}
                    timeRangeData={[]}
                    tagsData={[]}
                    stats={{}}
                    parameters={{}}
                    getAuthorsAndTimeRangeData={sinon.spy()}
                />,
            );

            expect(
                wrapper.find('.visibility-switch').hasClass(filter.slug),
            ).toBeTruthy();
        }
    });
});
