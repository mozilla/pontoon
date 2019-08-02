import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { FiltersPanelBase } from './FiltersPanel';
import { FILTERS_STATUS } from '..';


describe('<FiltersPanelBase>', () => {
    it('shows a panel with filters on click', () => {
        const statuses = {};
        const extras = {};
        const stats = {};
        const wrapper = shallow(
            <FiltersPanelBase
                statuses={ statuses }
                extras={ extras }
                stats={ stats }
            />
        );

        expect(wrapper.find('div.menu')).toHaveLength(0);
        wrapper.find('.visibility-switch').simulate('click');
        expect(wrapper.find('div.menu')).toHaveLength(1);
    });

    it('has the correct icon based on parameters', () => {
        for (let filter of FILTERS_STATUS) {
            const statuses = {
                [filter.slug]: true,
            };
            const extras = {};
            const stats = {};

            const wrapper = shallow(
                <FiltersPanelBase
                    statuses={ statuses }
                    extras={ extras }
                    stats={ stats }
                />
            );

            expect(
                wrapper.find('.visibility-switch').hasClass(filter.slug)
            ).toBeTruthy();
        }
    });

    it('correctly sets statuses as selected', () => {
        const statuses = {
            warnings: true,
            errors: false,
            missing: true,
        };
        const extras = {};
        const stats = {};
        const wrapper = shallow(
            <FiltersPanelBase
                statuses={ statuses }
                extras={ extras }
                stats={ stats }
            />
        );

        wrapper.find('.visibility-switch').simulate('click');

        for (let filter of FILTERS_STATUS) {
            if (statuses[filter.slug]) {
                expect(
                    wrapper.find(`.menu .${filter.slug}`).hasClass('selected')
                ).toBeTruthy();
            }
            else {
                expect(
                    wrapper.find(`.menu .${filter.slug}`).hasClass('selected')
                ).toBeFalsy();
            }
        }
    });

    it('sets a single status on click on a status title', () => {
        let setSingleStatus;

        for (let filter of FILTERS_STATUS) {
            const statuses = {
                [filter.slug]: true,
            };
            const extras = {};
            const stats = {};
            setSingleStatus = sinon.spy()

            const wrapper = shallow(
                <FiltersPanelBase
                    stats={ stats }
                    statuses={ statuses }
                    extras={ extras }
                    setSingleStatus= { setSingleStatus }
                />
            );
            wrapper.find('.visibility-switch').simulate('click');
            wrapper.find(`.menu .${filter.slug}`).simulate('click');

            expect(setSingleStatus.calledWith(filter.slug)).toBeTruthy();
        }
    });

    it('selects a status on click on a status icon', () => {
        let toggleStatus;

        for (let filter of FILTERS_STATUS) {
            const statuses = {
                [filter.slug]: false,
            };
            const extras = {};
            const stats = {};
            toggleStatus = sinon.spy()

            const wrapper = shallow(
                <FiltersPanelBase
                    stats={ stats }
                    statuses={ statuses }
                    extras={ extras }
                    toggleStatus= { toggleStatus }
                />
            );
            wrapper.find('.visibility-switch').simulate('click');
            wrapper.find(`.menu .${filter.slug} .status`).simulate(
                'click',
                { stopPropagation: sinon.fake() }
            );

            if (filter.slug === 'all') {
                expect(toggleStatus.called).toBeFalsy();
            }
            else {
                expect(toggleStatus.calledWith(filter.slug)).toBeTruthy();
            }
        }
    });

    it('hides the toolbar when no filters are selected', () => {
        const statuses = {
            warnings: false,
            errors: false,
            missing: false,
        };
        const extras = {};
        const stats = {};
        const wrapper = shallow(
            <FiltersPanelBase
                statuses={ statuses }
                extras={ extras }
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
        const extras = {};
        const stats = {};
        const wrapper = shallow(
            <FiltersPanelBase
                statuses={ statuses }
                extras={ extras }
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
        const extras = {};
        const stats = {};
        const wrapper = shallow(
            <FiltersPanelBase
                statuses={ statuses }
                extras={ extras }
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
        const extras = {};
        const stats = {};
        const wrapper = shallow(
            <FiltersPanelBase
                statuses={ statuses }
                extras={ extras }
                stats={ stats }
                update={ update }
            />
        );

        wrapper.find('.visibility-switch').simulate('click');
        wrapper.find('.toolbar .apply-selected').simulate('click');

        expect(update.called).toBeTruthy();
    });
});
