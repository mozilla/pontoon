import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget, sleep } from 'test/utils';

import { actions } from 'core/navigation';
import SearchBox, { SearchBoxBase } from './SearchBox';
import { FILTERS_STATUS } from '..';


describe('<SearchBoxBase>', () => {
    it('shows a search input', () => {
        const params = {
            search: '',
        };
        const wrapper = shallow(<SearchBoxBase parameters={ params } />);

        expect(wrapper.find('input#search')).toHaveLength(1);
    });

    it('has the correct placeholder based on parameters', () => {
        for (let filter of FILTERS_STATUS) {
            const params = { status: filter.tag };
            const wrapper = shallow(<SearchBoxBase parameters={ params } />);
            expect(wrapper.find('input#search').prop('placeholder')).toContain(filter.title);
        }
    });
});


describe('<SearchBox>', () => {
    it('updates the search text after a delay', () => {
        const store = createReduxStore();
        const wrapper = shallowUntilTarget(
            <SearchBox store={ store } />,
            SearchBoxBase
        );

        const updateSpy = sinon.spy(actions, 'updateSearch');

        const event = { currentTarget: { value: 'test' } };
        wrapper.find('input#search').simulate('change', event);

        // The state has been updated correctly...
        expect(wrapper.state().search).toEqual('test');

        // ... but it wasn't propagated to the global redux store yet.
        expect(updateSpy.calledOnce).toBeFalsy();

        // Wait for 500ms until the debounce delay has passed.
        return sleep(500).then(() => {
            expect(updateSpy.calledOnce).toBeTruthy();
        });
    });
});
