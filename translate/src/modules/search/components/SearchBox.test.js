import { mount, shallow } from 'enzyme';
import { createMemoryHistory } from 'history';
import React from 'react';
import { act } from 'react-dom/test-utils';
import sinon from 'sinon';

import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { FILTERS_EXTRA, FILTERS_STATUS } from '../constants';
import SearchBox, { SearchBoxBase } from './SearchBox';

const PROJECT = {
  tags: [],
};

const SEARCH_AND_FILTERS = {
  authors: [],
  countsPerMinute: [],
};

describe('<SearchBoxBase>', () => {
  it('shows a search input', () => {
    const params = {
      search: '',
    };
    const wrapper = shallow(
      <SearchBoxBase
        parameters={params}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
      />,
    );

    expect(wrapper.find('input#search')).toHaveLength(1);
  });

  it('has the correct placeholder based on parameters', () => {
    for (let { name, slug } of FILTERS_STATUS) {
      const wrapper = mount(
        <SearchBoxBase
          parameters={{ status: slug }}
          project={PROJECT}
          searchAndFilters={SEARCH_AND_FILTERS}
        />,
      );
      expect(wrapper.find('input#search').prop('placeholder')).toContain(name);
    }

    for (let { name, slug } of FILTERS_EXTRA) {
      const wrapper = mount(
        <SearchBoxBase
          parameters={{ extra: slug }}
          project={PROJECT}
          searchAndFilters={SEARCH_AND_FILTERS}
        />,
      );
      expect(wrapper.find('input#search').prop('placeholder')).toContain(name);
    }
  });

  it('empties the search field after navigation parameter "search" gets removed', () => {
    const wrapper = mount(
      <SearchBoxBase
        parameters={{ search: 'search' }}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
      />,
    );

    expect(wrapper.find('input').prop('value')).toEqual('search');

    wrapper.setProps({ parameters: { search: null } });
    wrapper.update();

    expect(wrapper.find('input').prop('value')).toEqual('');
  });

  it('toggles a filter', () => {
    const wrapper = mount(
      <SearchBoxBase
        parameters={{}}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
      />,
    );

    expect(wrapper.find('FiltersPanelBase').prop('filters').statuses).toEqual(
      [],
    );

    act(() => {
      wrapper.find('FiltersPanelBase').prop('toggleFilter')(
        'missing',
        'statuses',
      );
    });
    wrapper.update();

    expect(wrapper.find('FiltersPanelBase').prop('filters').statuses).toEqual([
      'missing',
    ]);
  });

  it('sets a single filter', () => {
    const wrapper = mount(
      <SearchBoxBase
        dispatch={() => {}}
        parameters={{}}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
        store={{ getState: () => ({ unsavedchanges: {} }) }}
      />,
    );

    act(() => {
      const { toggleFilter, applySingleFilter } = wrapper
        .find('FiltersPanelBase')
        .props();
      toggleFilter('missing', 'statuses');
      applySingleFilter('warnings', 'statuses');
    });
    wrapper.update();

    expect(wrapper.find('FiltersPanelBase').prop('filters').statuses).toEqual([
      'warnings',
    ]);
  });

  it('sets multiple & resets to initial statuses', () => {
    const wrapper = mount(
      <SearchBoxBase
        parameters={{}}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
      />,
    );

    act(() => {
      const toggle = wrapper.find('FiltersPanelBase').prop('toggleFilter');
      toggle('warnings', 'statuses');
      toggle('rejected', 'extras');
    });
    wrapper.update();

    act(() => {
      const toggle = wrapper.find('FiltersPanelBase').prop('toggleFilter');
      toggle('errors', 'statuses');
    });
    wrapper.update();

    expect(wrapper.find('FiltersPanelBase').prop('filters')).toMatchObject({
      extras: ['rejected'],
      statuses: ['warnings', 'errors'],
    });

    act(() => {
      wrapper.find('FiltersPanelBase').prop('resetFilters')();
    });
    wrapper.update();

    expect(wrapper.find('FiltersPanelBase').prop('filters')).toMatchObject({
      extras: [],
      statuses: [],
    });
  });

  it('sets status to null when "all" is selected', () => {
    const push = sinon.spy();
    const wrapper = mount(
      <SearchBoxBase
        dispatch={(a) => (typeof a === 'function' ? a() : {})}
        parameters={{ push }}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
        store={{ getState: () => ({ unsavedchanges: {} }) }}
      />,
    );

    act(() => {
      const apply = wrapper.find('FiltersPanelBase').prop('applySingleFilter');
      apply('all', 'statuses');
    });
    wrapper.update();

    expect(push.callCount).toBe(1);
    expect(push.firstCall.args).toMatchObject([
      {
        author: '',
        extra: '',
        search: '',
        status: null,
        tag: '',
        time: null,
        entity: 0,
      },
    ]);
  });

  it('sets correct status', () => {
    const push = sinon.spy();
    const wrapper = mount(
      <SearchBoxBase
        dispatch={(a) => (typeof a === 'function' ? a() : {})}
        parameters={{ push }}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
        store={{ getState: () => ({ unsavedchanges: {} }) }}
      />,
    );

    act(() => {
      const panel = wrapper.find('FiltersPanelBase');
      const toggle = panel.prop('toggleFilter');
      const setTimeRange = panel.prop('setTimeRange');
      toggle('missing', 'statuses');
      toggle('unchanged', 'extras');
      toggle('browser', 'tags');
      toggle('user@example.com', 'authors');
      setTimeRange('111111111111-111111111111');
    });
    wrapper.update();

    act(() => {
      const toggle = wrapper.find('FiltersPanelBase').prop('toggleFilter');
      toggle('warnings', 'statuses');
    });
    wrapper.update();

    const apply = wrapper.find('FiltersPanelBase').prop('applyFilters');
    apply();

    expect(
      push.calledWith({
        author: 'user@example.com',
        extra: 'unchanged',
        search: '',
        status: 'missing,warnings',
        tag: 'browser',
        time: '111111111111-111111111111',
        entity: 0,
      }),
    ).toBeTruthy();
  });
});

describe('<SearchBox>', () => {
  it('updates the search text after a delay', () => {
    const history = createMemoryHistory({
      initialEntries: ['/kg/firefox/all-resources/'],
    });
    const spy = sinon.spy();
    history.listen(spy);

    const store = createReduxStore();
    const wrapper = mountComponentWithStore(SearchBox, store, {}, history);

    // `simulate()` doesn't quite work in conjunction with `mount()`, so
    // invoking the `prop()` callback directly is the way to go as suggested
    // by the enzyme maintainer...
    act(() => {
      wrapper.find('input#search').prop('onChange')({
        currentTarget: { value: 'test' },
      });
    });
    wrapper.update();

    //console.log(wrapper.find('input#search').props())
    // The state has been updated correctly...
    expect(wrapper.find('input#search').prop('value')).toEqual('test');

    // ... but it wasn't propagated to the global redux store yet.
    expect(spy.callCount).toBe(0);

    // Wait until Enter is pressed.
    wrapper.find('input#search').simulate('keydown', { key: 'Enter' });

    expect(spy.callCount).toBe(1);
    expect(spy.firstCall.args).toMatchObject([
      {
        pathname: '/kg/firefox/all-resources/',
        search: '?search=test',
        hash: '',
      },
      'PUSH',
    ]);
  });

  it('puts focus on the search input on Ctrl + Shift + F', () => {
    const wrapper = mount(
      <SearchBoxBase
        parameters={{ search: '' }}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
      />,
    );

    const focusMock = sinon.spy(
      wrapper.find('input#search').instance(),
      'focus',
    );
    document.dispatchEvent(
      new KeyboardEvent('keydown', {
        key: 'F',
        ctrlKey: true,
        shiftKey: true,
      }),
    );

    expect(focusMock.calledOnce).toBeTruthy();
  });
});
