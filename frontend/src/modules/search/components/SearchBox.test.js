import React from 'react';
import { mount, shallow } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

import { actions } from 'core/navigation';
import SearchBox, { SearchBoxBase } from './SearchBox';
import { FILTERS_STATUS, FILTERS_EXTRA } from '..';


const FILTERS = [].concat(
    FILTERS_STATUS,
    FILTERS_EXTRA,
);


const PROJECT = {
    tags: [],
}


const SEARCH_AND_FILTERS = {
    authors: [],
    countsPerMinute: [],
}


describe('<SearchBoxBase>', () => {
    beforeAll(() => {
        sinon.stub(actions, 'update').returns({ type: 'whatever'});
    });

    afterEach(() => {
        actions.update.reset();
    });

    afterAll(() => {
        actions.update.restore();
    });

    it('shows a search input', () => {
        const params = {
            search: '',
        };
        const wrapper = shallow(<SearchBoxBase
            parameters={ params }
            project={ PROJECT }
            searchAndFilters={ SEARCH_AND_FILTERS }
        />);

        expect(wrapper.find('input#search')).toHaveLength(1);
    });

    it('has the correct placeholder based on parameters', () => {
        for (let filter of FILTERS) {
            let params;

            if (FILTERS_STATUS.includes(filter)) {
                params = { status: filter.slug };
            }
            else if (FILTERS_EXTRA.includes(filter)) {
                params = { extra: filter.slug };
            }

            const wrapper = shallow(<SearchBoxBase
                parameters={ params }
                project={ PROJECT }
                searchAndFilters={ SEARCH_AND_FILTERS }
            />);
            expect(wrapper.find('input#search').prop('placeholder')).toContain(filter.name);
        }
    });

    it('empties the search field after navigation parameter "search" gets removed', () => {
        const params = {
            search: 'search',
        };
        const wrapper = shallow(<SearchBoxBase
            parameters={ params }
            project={ PROJECT }
            searchAndFilters={ SEARCH_AND_FILTERS }
        />);

        wrapper.setProps({
            parameters: {
                search: null,
            },
        });

        expect(wrapper.state().search).toEqual('');
    });

    it('returns correct list of selected statuses', () => {
        const wrapper = shallow(<SearchBoxBase
            parameters={ {} }
            project={ PROJECT }
            searchAndFilters={ SEARCH_AND_FILTERS }
        />);

        wrapper.setState({
            statuses: {
                warnings: true,
                errors: true,
                missing: false,
            }
        });

        const selected = wrapper.instance().getSelectedStatuses();
        expect(selected).toEqual([ 'warnings', 'errors' ]);
    });

    it('returns correct list of selected extras', () => {
        const wrapper = shallow(<SearchBoxBase
            parameters={ {} }
            project={ PROJECT }
            searchAndFilters={ SEARCH_AND_FILTERS }
        />);

        wrapper.setState({
            extras: {
                unchanged: true,
                rejected: false,
            }
        });

        const selected = wrapper.instance().getSelectedExtras();
        expect(selected).toEqual(['unchanged']);
    });

    it('toggles a filter', () => {
        const wrapper = shallow(<SearchBoxBase
            parameters={ {} }
            project={ PROJECT }
            searchAndFilters={ SEARCH_AND_FILTERS }
        />);

        wrapper.setState({ statuses: { missing: false } });
        expect(wrapper.state('statuses').missing).toBeFalsy();

        wrapper.instance().toggleFilter('missing', 'statuses');
        expect(wrapper.state('statuses').missing).toBeTruthy();
    });

    it('sets a single filter', () => {
        const wrapper = shallow(<SearchBoxBase
            parameters={ {} }
            project={ PROJECT }
            searchAndFilters={ SEARCH_AND_FILTERS }
        />);

        wrapper.setState({
            statuses: {
                warnings: true,
                errors: false,
                missing: false,
            }
        });
        expect(wrapper.state('statuses').warnings).toBeTruthy();
        expect(wrapper.state('statuses').errors).toBeFalsy();
        expect(wrapper.state('statuses').missing).toBeFalsy();

        wrapper.instance().applySingleFilter('missing', 'statuses');
        expect(wrapper.state('statuses').warnings).toBeFalsy();
        expect(wrapper.state('statuses').errors).toBeFalsy();
        expect(wrapper.state('statuses').missing).toBeTruthy();
    });

    it('resets to initial statuses', () => {
        const wrapper = shallow(<SearchBoxBase
            parameters={ {} }
            project={ PROJECT }
            searchAndFilters={ SEARCH_AND_FILTERS }
        />);

        wrapper.setState({
            statuses: {
                warnings: true,
                errors: true,
                missing: false,
            },
            extras: {
                unchanged: false,
                rejected: true,
            }
        });

        wrapper.instance().resetFilters();
        expect(wrapper.state('statuses').warnings).toBeFalsy();
        expect(wrapper.state('statuses').errors).toBeFalsy();
        expect(wrapper.state('statuses').missing).toBeFalsy();
        expect(wrapper.state('extras').unchanged).toBeFalsy();
        expect(wrapper.state('extras').rejected).toBeFalsy();
    });

    it('sets status to null when "all" is selected', () => {
        const wrapper = shallow(<SearchBoxBase
            parameters={ {} }
            project={ PROJECT }
            searchAndFilters={ SEARCH_AND_FILTERS }
            router={ {} }
            dispatch={ () => {} }
        />);
        wrapper.setState({ statuses: { all: true } });

        wrapper.instance()._update();
        expect(
            actions.update.calledWith({}, {
                status: null,
                extra: '',
                tag: '',
                time: '',
                author: '',
                search: '',
            })
        ).toBeTruthy();
    });

    it('sets correct status', () => {
        const wrapper = shallow(<SearchBoxBase
            parameters={ {} }
            project={ PROJECT }
            searchAndFilters={ SEARCH_AND_FILTERS }
            router={ {} }
            dispatch={ () => {} }
        />);
        wrapper.setState({
            statuses: { missing: true, warnings: true },
            extras: { unchanged: true },
            tags: { browser: true },
            timeRange: { from: '111111111111', to: '111111111111' },
            authors: { 'user@example.com': true },
        });

        wrapper.instance()._update();
        expect(
            actions.update.calledWith({}, {
                status: 'missing,warnings',
                extra: 'unchanged',
                tag: 'browser',
                time: '111111111111-111111111111',
                author: 'user@example.com',
                search: '',
            })
        ).toBeTruthy();
    });
});


describe('<SearchBox>', () => {
    it('updates the search text after a delay', () => {
        const store = createReduxStore();
        const wrapper = shallowUntilTarget(
            <SearchBox store={ store } />,
            SearchBoxBase
        );

        const updateSpy = sinon.spy(actions, 'update');

        const inputChanged = { currentTarget: { value: 'test' } };
        wrapper.find('input#search').simulate('change', inputChanged);

        // The state has been updated correctly...
        expect(wrapper.state().search).toEqual('test');

        // ... but it wasn't propagated to the global redux store yet.
        expect(updateSpy.calledOnce).toBeFalsy();

        // Wait until Enter is pressed.
        const enterPressed = { keyCode: 13 };
        wrapper.find('input#search').simulate('keydown', enterPressed);
        expect(updateSpy.calledOnce).toBeTruthy();
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
        const wrapper = mount(<SearchBoxBase
            parameters={ params }
            project={ PROJECT }
            searchAndFilters={ SEARCH_AND_FILTERS }
        />);
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
