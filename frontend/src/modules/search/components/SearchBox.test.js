import React from 'react';
import { mount, shallow } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget, sleep } from 'test/utils';

import { actions } from 'core/navigation';
import SearchBox, { SearchBoxBase } from './SearchBox';
import { FILTERS_STATUS } from '..';


describe('<SearchBoxBase>', () => {
    beforeAll(() => {
        sinon.stub(actions, 'updateStatus').returns({ type: 'whatever'});
    });

    afterEach(() => {
        actions.updateStatus.reset();
    });

    afterAll(() => {
        actions.updateStatus.restore();
    });

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

    it('empties the search field after navigation parameter "search" gets removed', () => {
        const params = {
            search: 'search',
        };
        const wrapper = shallow(<SearchBoxBase parameters={ params } />);

        wrapper.setProps({
            parameters: {
                search: null,
            },
        });

        expect(wrapper.state().search).toEqual('');
    });

    it('returns correct list of selected statuses', () => {
        const wrapper = shallow(<SearchBoxBase parameters={ {} } />);

        wrapper.setState({
            statuses: {
                warnings: true,
                errors: true,
                missing: false,
            }
        });

        const selected = wrapper.instance().getSelectedStatuses();
        expect(selected).toEqual(['warnings', 'errors']);
    });

    it('toggles a status', () => {
        const wrapper = shallow(<SearchBoxBase parameters={ {} } />);
        wrapper.setState({ statuses: { missing: false } });

        wrapper.instance().toggleStatus('missing');

        expect(wrapper.state('statuses').missing).toBeTruthy();
    });

    it('sets a single status', () => {
        const wrapper = shallow(<SearchBoxBase parameters={ {} } />);

        wrapper.setState({
            statuses: {
                warnings: true,
                errors: true,
                missing: false,
            }
        });

        wrapper.instance().setSingleStatus('missing');
        expect(wrapper.state('statuses').warnings).toBeFalsy();
        expect(wrapper.state('statuses').errors).toBeFalsy();
        expect(wrapper.state('statuses').missing).toBeTruthy();
    });

    it('resets to initial statuses', () => {
        const wrapper = shallow(<SearchBoxBase parameters={ {} } />);

        wrapper.setState({
            statuses: {
                warnings: true,
                errors: true,
                missing: false,
            }
        });

        wrapper.instance().resetStatuses();
        expect(wrapper.state('statuses').warnings).toBeFalsy();
        expect(wrapper.state('statuses').errors).toBeFalsy();
        expect(wrapper.state('statuses').missing).toBeFalsy();
    });

    it('sets status to null when "all" is selected', () => {
        const wrapper = shallow(<SearchBoxBase
            parameters={ {} }
            router={ {} }
            dispatch={ () => {} }
        />);
        wrapper.setState({ statuses: { all: true } });

        wrapper.instance().updateStatus();
        expect(actions.updateStatus.calledWith({}, null)).toBeTruthy();
    });

    it('sets correct status', () => {
        const wrapper = shallow(<SearchBoxBase
            parameters={ {} }
            router={ {} }
            dispatch={ () => {} }
        />);
        wrapper.setState({ statuses: { missing: true, warnings: true } });

        wrapper.instance().updateStatus();
        expect(actions.updateStatus.calledWith({}, 'missing,warnings')).toBeTruthy();
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

    it('puts focus on the search input on Ctrl + Shift + F', () => {
        // Simulating the key presses on `document`.
        // See https://github.com/airbnb/enzyme/issues/426
        const eventsMap = {};
        document.addEventListener = sinon.spy((event, cb) => {
            eventsMap[event] = cb;
        });

        const params = {
            search: '',
        };
        const wrapper = mount(<SearchBoxBase parameters={ params } />);
        const searchInput = wrapper.instance().searchInput;

        const focusMock = sinon.spy(searchInput.current, 'focus');
        expect(focusMock.calledOnce).toBeFalsy();
        const event = {
            preventDefault: sinon.spy(),
            keyCode: 70,  // Up
            altKey: false,
            ctrlKey: true,
            shiftKey: true,
        };
        eventsMap.keydown(event);
        expect(focusMock.calledOnce).toBeTruthy();
    });
});
