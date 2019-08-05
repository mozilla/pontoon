import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { FiltersPanelBase } from './FiltersPanel';
import { FILTERS_STATUS, FILTERS_EXTRA } from '..';


const FILTERS = [].concat(
    FILTERS_STATUS,
    FILTERS_EXTRA,
);


describe('<FiltersPanelBase>', () => {
    it('shows a panel with filters on click', () => {
        const statuses = {};
        const extras = {};
        const tags = {};
        const stats = {};
        const tagsData = [];
        const wrapper = shallow(
            <FiltersPanelBase
                statuses={ statuses }
                extras={ extras }
                tags={ tags }
                tagsData={ tagsData }
                stats={ stats }
            />
        );

        expect(wrapper.find('div.menu')).toHaveLength(0);
        wrapper.find('.visibility-switch').simulate('click');
        expect(wrapper.find('div.menu')).toHaveLength(1);
    });

    it('has the correct icon based on parameters', () => {
        const tags = {};
        const stats = {};
        const tagsData = [];

        for (let filter of FILTERS) {
            let statuses = {};
            let extras = {};

            const value = {
                [filter.slug]: true,
            };

            if (FILTERS_STATUS.includes(filter)) {
                statuses = value;
            }
            else if (FILTERS_EXTRA.includes(filter)) {
                extras = value;
            }

            const wrapper = shallow(
                <FiltersPanelBase
                    statuses={ statuses }
                    extras={ extras }
                    tags={ tags }
                    tagsData={ tagsData }
                    stats={ stats }
                />
            );

            expect(
                wrapper.find('.visibility-switch').hasClass(filter.slug)
            ).toBeTruthy();
        }
    });

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

        const tags = {};
        const stats = {};
        const tagsData = [];

        const wrapper = shallow(
            <FiltersPanelBase
                statuses={ statuses }
                extras={ extras }
                tags={ tags }
                tagsData={ tagsData }
                stats={ stats }
            />
        );

        wrapper.find('.visibility-switch').simulate('click');

        for (let filter of FILTERS) {
            let isFilterSelected;

            if (FILTERS_STATUS.includes(filter)) {
                isFilterSelected = statuses[filter.slug];
            }
            else if (FILTERS_EXTRA.includes(filter)) {
                isFilterSelected = extras[filter.slug];
            }

            const isClassSet = wrapper.find(`.menu .${filter.slug}`).hasClass('selected');

            if (isFilterSelected) {
                expect(isClassSet).toBeTruthy();
            }
            else {
                expect(isClassSet).toBeFalsy();
            }
        }
    });

    it('applies a single filter on click on a filter title', () => {
        let applySingleFilter;
        const tags = {};
        const stats = {};
        const tagsData = [];

        for (let filter of FILTERS) {
            let statuses = {};
            let extras = {};

            const value = {
                [filter.slug]: true,
            };

            if (FILTERS_STATUS.includes(filter)) {
                statuses = value;
            }
            else if (FILTERS_EXTRA.includes(filter)) {
                extras = value;
            }

            applySingleFilter = sinon.spy()

            const wrapper = shallow(
                <FiltersPanelBase
                    statuses={ statuses }
                    extras={ extras }
                    tags={ tags }
                    tagsData={ tagsData }
                    stats={ stats }
                    applySingleFilter= { applySingleFilter }
                />
            );
            wrapper.find('.visibility-switch').simulate('click');
            wrapper.find(`.menu .${filter.slug}`).simulate('click');

            expect(applySingleFilter.calledWith(filter.slug)).toBeTruthy();
        }
    });

    it('toggles a filter on click on a filter status icon', () => {
        let toggleFilter;
        const tags = {};
        const stats = {};
        const tagsData = [];

        for (let filter of FILTERS) {
            let statuses = {};
            let extras = {};

            const value = {
                [filter.slug]: false,
            };

            if (FILTERS_STATUS.includes(filter)) {
                statuses = value;
            }
            else if (FILTERS_EXTRA.includes(filter)) {
                extras = value;
            }

            toggleFilter = sinon.spy()

            const wrapper = shallow(
                <FiltersPanelBase
                    statuses={ statuses }
                    extras={ extras }
                    tags={ tags }
                    tagsData={ tagsData }
                    stats={ stats }
                    toggleFilter= { toggleFilter }
                />
            );
            wrapper.find('.visibility-switch').simulate('click');
            wrapper.find(`.menu .${filter.slug} .status`).simulate(
                'click',
                { stopPropagation: sinon.fake() }
            );

            if (filter.slug === 'all') {
                expect(toggleFilter.called).toBeFalsy();
            }
            else {
                expect(toggleFilter.calledWith(filter.slug)).toBeTruthy();
            }
        }
    });

    it('hides the toolbar when no filters are selected', () => {
        const statuses = {
            warnings: false,
            errors: false,
            missing: false,
        };
        const extras = {
            unchanged: false,
            rejected: false,
        };
        const tags = {};
        const stats = {};
        const tagsData = [];
        const wrapper = shallow(
            <FiltersPanelBase
                statuses={ statuses }
                extras={ extras }
                tags={ tags }
                tagsData={ tagsData }
                stats={ stats }
            />
        );

        wrapper.find('.visibility-switch').simulate('click');
        expect(wrapper.find('.toolbar')).toHaveLength(0);
    });

    it('shows the toolbar when some filters are selected', () => {
        const statuses = {
            warnings: false,
            errors: true,
            missing: true,
        };
        const extras = {
            unchanged: false,
            rejected: true,
        };
        const tags = {};
        const stats = {};
        const tagsData = [];
        const wrapper = shallow(
            <FiltersPanelBase
                statuses={ statuses }
                extras={ extras }
                tags={ tags }
                tagsData={ tagsData }
                stats={ stats }
            />
        );

        wrapper.find('.visibility-switch').simulate('click');
        expect(wrapper.find('.toolbar')).toHaveLength(1);
    });

    it('resets selected filters on click on the Clear button', () => {
        const resetFilters = sinon.spy();

        const statuses = {
            warnings: false,
            errors: true,
        };
        const extras = {
            unchanged: false,
            rejected: true,
        };
        const tags = {};
        const stats = {};
        const tagsData = [];
        const wrapper = shallow(
            <FiltersPanelBase
                statuses={ statuses }
                extras={ extras }
                tags={ tags }
                tagsData={ tagsData }
                stats={ stats }
                resetFilters={ resetFilters }
            />
        );

        wrapper.find('.visibility-switch').simulate('click');
        wrapper.find('.toolbar .clear-selection').simulate('click');

        expect(resetFilters.called).toBeTruthy();
    });

    it('applies selected filters on click on the Apply button', () => {
        const update = sinon.spy();

        const statuses = {
            warnings: false,
            errors: true,
        };
        const extras = {
            unchanged: false,
            rejected: true,
        };
        const tags = {};
        const stats = {};
        const tagsData = [];
        const wrapper = shallow(
            <FiltersPanelBase
                statuses={ statuses }
                extras={ extras }
                tags={ tags }
                tagsData={ tagsData }
                stats={ stats }
                update={ update }
            />
        );

        wrapper.find('.visibility-switch').simulate('click');
        wrapper.find('.toolbar .apply-selected').simulate('click');

        expect(update.called).toBeTruthy();
    });
});
