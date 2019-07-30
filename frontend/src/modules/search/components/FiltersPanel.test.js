import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { FiltersPanelBase } from './FiltersPanel';
import { FILTERS_STATUS } from '..';


describe('<FiltersPanelBase>', () => {
    it('shows a panel with filters on click', () => {
        const statuses = {};
        const stats = {};
        const wrapper = shallow(
            <FiltersPanelBase statuses={ statuses } stats={ stats } />
        );

        expect(wrapper.find('div.menu')).toHaveLength(0);
        wrapper.find('.visibility-switch').simulate('click');
        expect(wrapper.find('div.menu')).toHaveLength(1);
    });

    it('has the correct icon based on parameters', () => {
        for (let filter of FILTERS_STATUS) {
            const statuses = {
                [filter.tag]: true,
            };
            const stats = {};

            const wrapper = shallow(
                <FiltersPanelBase statuses={ statuses } stats={ stats } />
            );

            expect(
                wrapper.find('.visibility-switch').hasClass(filter.tag)
            ).toBeTruthy();
        }
    });

    it('correctly sets statuses as selected', () => {
        const statuses = {
            warnings: true,
            errors: false,
            missing: true,
        };
        const stats = {};
        const wrapper = shallow(
            <FiltersPanelBase statuses={ statuses } stats={ stats } />
        );

        wrapper.find('.visibility-switch').simulate('click');

        for (let filter of FILTERS_STATUS) {
            if (statuses[filter.tag]) {
                expect(
                    wrapper.find(`.menu .${filter.tag}`).hasClass('selected')
                ).toBeTruthy();
            }
            else {
                expect(
                    wrapper.find(`.menu .${filter.tag}`).hasClass('selected')
                ).toBeFalsy();
            }
        }
    });

    it('sets a single status on click on a status title', () => {
        let setSingleStatus;

        for (let filter of FILTERS_STATUS) {
            const statuses = {
                [filter.tag]: true,
            };
            const stats = {};
            setSingleStatus = sinon.spy()

            const wrapper = shallow(
                <FiltersPanelBase
                    stats={ stats }
                    statuses={ statuses }
                    setSingleStatus= { setSingleStatus }
                />
            );
            wrapper.find('.visibility-switch').simulate('click');
            wrapper.find(`.menu .${filter.tag}`).simulate('click');

            expect(setSingleStatus.calledWith(filter.tag)).toBeTruthy();
        }
    });

    it('selects a status on click on a status icon', () => {
        let toggleStatus;

        for (let filter of FILTERS_STATUS) {
            const statuses = {
                [filter.tag]: false,
            };
            const stats = {};
            toggleStatus = sinon.spy()

            const wrapper = shallow(
                <FiltersPanelBase
                    stats={ stats }
                    statuses={ statuses }
                    toggleStatus= { toggleStatus }
                />
            );
            wrapper.find('.visibility-switch').simulate('click');
            wrapper.find(`.menu .${filter.tag} .status`).simulate(
                'click',
                { stopPropagation: sinon.fake() }
            );

            if (filter.tag === 'all') {
                expect(toggleStatus.called).toBeFalsy();
            }
            else {
                expect(toggleStatus.calledWith(filter.tag)).toBeTruthy();
            }
        }
    });

    it('hides the toolbar when no filters are selected', () => {
        const statuses = {
            warnings: false,
            errors: false,
            missing: false,
        };
        const stats = {};
        const wrapper = shallow(
            <FiltersPanelBase statuses={ statuses } stats={ stats } />
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
        const stats = {};
        const wrapper = shallow(
            <FiltersPanelBase statuses={ statuses } stats={ stats } />
        );

        wrapper.find('.visibility-switch').simulate('click');
        expect(wrapper.find('.toolbar')).toHaveLength(1);
    });

    it('resets selected filters on click on the Clear button', () => {
        const resetStatuses = sinon.spy();

        const statuses = {
            warnings: false,
            errors: true,
        };
        const stats = {};
        const wrapper = shallow(
            <FiltersPanelBase
                statuses={ statuses }
                stats={ stats }
                resetStatuses={ resetStatuses }
            />
        );

        wrapper.find('.visibility-switch').simulate('click');
        wrapper.find('.toolbar .clear-selection').simulate('click');

        expect(resetStatuses.called).toBeTruthy();
    });

    it('applies selected filters on click on the Apply button', () => {
        const update = sinon.spy();

        const statuses = {
            warnings: false,
            errors: true,
        };
        const stats = {};
        const wrapper = shallow(
            <FiltersPanelBase
                statuses={ statuses }
                stats={ stats }
                update={ update }
            />
        );

        wrapper.find('.visibility-switch').simulate('click');
        wrapper.find('.toolbar .apply-selected').simulate('click');

        expect(update.called).toBeTruthy();
    });
});
