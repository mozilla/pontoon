import { mount, shallow } from 'enzyme';
import { createMemoryHistory } from 'history';
import React from 'react';
import { act } from 'react-dom/test-utils';
import { expect, vi } from 'vitest';

import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { FILTERS_EXTRA, FILTERS_STATUS } from '../constants';
import { SearchBox, SearchBoxBase } from './SearchBox';
import { fireEvent } from '@testing-library/react';

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
    for (const { name, slug } of FILTERS_STATUS) {
      const wrapper = mount(
        <SearchBoxBase
          parameters={{ status: slug }}
          project={PROJECT}
          searchAndFilters={SEARCH_AND_FILTERS}
        />,
      );
      expect(wrapper.find('input#search').prop('placeholder')).toContain(name);
    }

    for (const { name, slug } of FILTERS_EXTRA) {
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

    expect(wrapper.find('FiltersPanel').prop('filters').statuses).toEqual([]);

    act(() => {
      wrapper.find('FiltersPanel').prop('toggleFilter')('missing', 'statuses');
    });
    wrapper.update();

    expect(wrapper.find('FiltersPanel').prop('filters').statuses).toEqual([
      'missing',
    ]);
  });

  it('sets a single filter', () => {
    const wrapper = mount(
      <SearchBoxBase
        dispatch={() => {}}
        parameters={{ push() {} }}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
        store={{ getState: () => ({ unsavedchanges: {} }) }}
      />,
    );

    act(() => {
      const { toggleFilter, applySingleFilter } = wrapper
        .find('FiltersPanel')
        .props();
      toggleFilter('missing', 'statuses');
      applySingleFilter('warnings', 'statuses');
    });
    wrapper.update();

    expect(wrapper.find('FiltersPanel').prop('filters').statuses).toEqual([
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
      const toggle = wrapper.find('FiltersPanel').prop('toggleFilter');
      toggle('warnings', 'statuses');
      toggle('rejected', 'extras');
    });
    wrapper.update();

    act(() => {
      const toggle = wrapper.find('FiltersPanel').prop('toggleFilter');
      toggle('errors', 'statuses');
    });
    wrapper.update();

    expect(wrapper.find('FiltersPanel').prop('filters')).toMatchObject({
      extras: ['rejected'],
      statuses: ['warnings', 'errors'],
    });

    act(() => {
      wrapper.find('FiltersPanel').prop('resetFilters')();
    });
    wrapper.update();

    expect(wrapper.find('FiltersPanel').prop('filters')).toMatchObject({
      extras: [],
      statuses: [],
    });
  });

  it('sets status to null when "all" is selected', () => {
    const push = vi.fn();
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
      const apply = wrapper.find('FiltersPanel').prop('applySingleFilter');
      apply('all', 'statuses');
    });
    wrapper.update();

    expect(push).toHaveBeenCalledTimes(1);
    expect(push).toHaveBeenNthCalledWith(1, {
      author: '',
      extra: '',
      list: null,
      search: '',
      status: null,
      tag: '',
      time: null,
      entity: 0,
    });
  });

  it('sets correct status', () => {
    const push = vi.fn();
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
      const panel = wrapper.find('FiltersPanel');
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
      const toggle = wrapper.find('FiltersPanel').prop('toggleFilter');
      toggle('warnings', 'statuses');
    });
    wrapper.update();

    const apply = wrapper.find('FiltersPanel').prop('applyFilters');
    apply();

    expect(push).toHaveBeenCalledWith({
      author: 'user@example.com',
      extra: 'unchanged',
      search: '',
      status: 'missing,warnings',
      tag: 'browser',
      time: '111111111111-111111111111',
      entity: 0,
      list: null,
    });
  });

  it('applies profile default for search_identifiers when URL param is not provided', () => {
    const wrapper = mount(
      <SearchBoxBase
        parameters={{}}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
        searchDefaults={{ search_identifiers: true }}
      />,
    );
    wrapper.update();

    expect(
      wrapper.find('SearchPanel').prop('searchOptions').search_identifiers,
    ).toBe(true);
  });

  it('URL param takes precedence over profile default for search_identifiers', () => {
    const wrapper = mount(
      <SearchBoxBase
        parameters={{ search_identifiers: false }}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
        searchDefaults={{ search_identifiers: true }}
      />,
    );
    wrapper.update();

    expect(
      wrapper.find('SearchPanel').prop('searchOptions').search_identifiers,
    ).toBe(false);
  });

  it('falls back to global defaults when both URL params and profile settings are not provided', () => {
    const wrapper = mount(
      <SearchBoxBase
        parameters={{}}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
        // no searchDefaults → DEFAULT_SEARCH_OPTIONS used
      />,
    );
    wrapper.update();

    const opts = wrapper.find('SearchPanel').prop('searchOptions');
    expect(opts.search_match_case).toBe(false);
    expect(opts.search_match_whole_word).toBe(false);
    expect(opts.search_identifiers).toBe(false);
    expect(opts.search_rejected_translations).toBe(false);
    expect(opts.search_exclude_source_strings).toBe(false);
  });

  it('applies profile defaults for all search options when URL params are not provided', () => {
    const wrapper = mount(
      <SearchBoxBase
        parameters={{}}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
        searchDefaults={{
          search_match_case: true,
          search_match_whole_word: true,
          search_identifiers: true,
          search_rejected_translations: true,
          search_exclude_source_strings: true,
        }}
      />,
    );
    wrapper.update();

    const opts = wrapper.find('SearchPanel').prop('searchOptions');
    expect(opts.search_match_case).toBe(true);
    expect(opts.search_match_whole_word).toBe(true);
    expect(opts.search_identifiers).toBe(true);
    expect(opts.search_rejected_translations).toBe(true);
    expect(opts.search_exclude_source_strings).toBe(true);
  });

  it('uses global defaults (not profile defaults) for options absent from a URL with an active search', () => {
    // Loading a URL like ?search=foo (no parameters) should show
    // search_identifiers as false in the UI, matching what the backend uses,
    // even if the profile default is true.
    const wrapper = mount(
      <SearchBoxBase
        parameters={{ search: 'foo' }}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
        searchDefaults={{ search_identifiers: true }}
      />,
    );
    wrapper.update();

    expect(
      wrapper.find('SearchPanel').prop('searchOptions').search_identifiers,
    ).toBe(false);
  });

  it('encodes search options that differ from the global default, omits those matching it', () => {
    const push = vi.fn();
    const wrapper = mount(
      <SearchBoxBase
        dispatch={(a) => (typeof a === 'function' ? a() : {})}
        parameters={{ push, search: '' }}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
        searchDefaults={{
          search_match_case: true,
          search_identifiers: true,
        }}
        store={{ getState: () => ({ unsavedchanges: {} }) }}
      />,
    );
    wrapper.update();

    wrapper.find('SearchPanel').prop('applyOptions')();

    // Options differing from the default should be added to the URL as
    // parameters. Options matching the default should not.
    expect(push).toHaveBeenCalledOnce();
    const pushed = push.mock.calls[0][0];
    expect(pushed.search_match_case).toBe(true);
    expect(pushed.search_identifiers).toBe(true);
    expect(pushed.search_match_whole_word).toBeUndefined();
    expect(pushed.search_rejected_translations).toBeUndefined();
    expect(pushed.search_exclude_source_strings).toBeUndefined();
  });

  it('omits a search option from URL when user unchecks a profile-default-true option', () => {
    const push = vi.fn();
    const wrapper = mount(
      <SearchBoxBase
        dispatch={(a) => (typeof a === 'function' ? a() : {})}
        parameters={{ push, search: '', search_identifiers: true }}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
        searchDefaults={{ search_identifiers: true }}
        store={{ getState: () => ({ unsavedchanges: {} }) }}
      />,
    );
    wrapper.update();

    act(() => {
      wrapper.find('SearchPanel').prop('toggleOption')('search_identifiers');
    });
    wrapper.update();

    wrapper.find('SearchPanel').prop('applyOptions')();

    const pushed = push.mock.calls[0][0];
    expect(pushed.search_identifiers).toBeUndefined();
  });
});

describe('<SearchBox>', () => {
  it('updates the search text after a delay', () => {
    const history = createMemoryHistory({
      initialEntries: ['/kg/firefox/all-resources/'],
    });
    const spy = vi.fn();
    history.listen(spy);

    const store = createReduxStore();
    const { getByRole } = mountComponentWithStore(
      SearchBox,
      store,
      {},
      history,
    );

    act(() => {
      fireEvent.change(getByRole('searchbox'), {
        target: { value: 'test' },
      });
    });

    // The state has been updated correctly...
    expect(getByRole('searchbox')).toHaveValue('test');

    // ... but it wasn't propagated to the global redux store yet.
    expect(spy).not.toHaveBeenCalled();

    // Wait until Enter is pressed.
    fireEvent.keyDown(getByRole('searchbox'), {
      key: 'Enter',
      code: 'Enter',
    });

    expect(spy).toHaveBeenCalledTimes(2);
    expect(spy).toHaveBeenNthCalledWith(
      1,
      {
        key: expect.anything(),
        pathname: '/kg/firefox/all-resources/',
        search: '?search=test',
        hash: '',
        state: undefined,
      },
      'PUSH',
    );
  });

  it('puts focus on the search input on Ctrl + Shift + F', () => {
    const wrapper = mount(
      <SearchBoxBase
        parameters={{ search: '' }}
        project={PROJECT}
        searchAndFilters={SEARCH_AND_FILTERS}
      />,
    );

    const focusMock = vi.spyOn(
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

    expect(focusMock).toHaveBeenCalledOnce();
  });
});
