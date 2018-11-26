import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';

import { FiltersPanelBase } from './FiltersPanel';
import { FILTERS_STATUS } from '..';


describe('<FiltersPanelBase>', () => {
    it('shows a panel with filters on click', () => {
        const params = {};
        const stats = {};
        const wrapper = shallow(
            <FiltersPanelBase stats={ stats } parameters={ params } />
        );

        expect(wrapper.find('div.menu')).toHaveLength(0);
        wrapper.find('.visibility-switch').simulate('click');
        expect(wrapper.find('div.menu')).toHaveLength(1);
    });

    it('has the correct icon based on parameters', () => {
        for (let filter of FILTERS_STATUS) {
            const params = { status: filter.tag };
            const stats = {};

            const wrapper = shallow(
                <FiltersPanelBase stats={ stats } parameters={ params } />
            );

            expect(
                wrapper.find('.visibility-switch').hasClass(filter.tag)
            ).toBeTruthy();
        }
    });

    it('calls the update function on click on filters', () => {
        const selectStatusSpy = sinon.spy();

        for (let filter of FILTERS_STATUS) {
            const params = {};
            const stats = {};

            const wrapper = shallow(
                <FiltersPanelBase
                    stats={ stats }
                    parameters={ params }
                    selectStatus= { selectStatusSpy }
                />
            );
            wrapper.find('.visibility-switch').simulate('click');
            wrapper.find(`.menu .${filter.tag}`).simulate('click');

            if (filter.tag === 'all') {
                // When the filter is `all`, we pass `null` to remove the param
                // from the URL.
                expect(selectStatusSpy.calledWith(null)).toBeTruthy();
            }
            else {
                expect(selectStatusSpy.calledWith(filter.tag)).toBeTruthy();
            }
        }
    });
});
