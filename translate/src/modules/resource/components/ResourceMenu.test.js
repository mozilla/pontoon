import { mount } from 'enzyme';
import { createMemoryHistory } from 'history';
import React from 'react';
import { act } from 'react-dom/test-utils';
import { Provider } from 'react-redux';

import { LocationProvider } from '~/context/Location';

import { createReduxStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { ResourceItem } from './ResourceItem';
import { ResourceMenu } from './ResourceMenu';

function createResourceMenu({
  project = 'project',
  resource = 'path/to.file',
} = {}) {
  const store = createReduxStore({
    resource: {
      allResources: {},
      resources: [
        { path: 'resourceAbc' },
        { path: 'resourceBcd' },
        { path: 'resourceCde' },
      ],
    },
  });
  const history = createMemoryHistory({
    initialEntries: [`/locale/${project}/${resource}/`],
  });
  return mount(
    <Provider store={store}>
      <LocationProvider history={history}>
        <MockLocalizationProvider>
          <ResourceMenu />
        </MockLocalizationProvider>
      </LocationProvider>
    </Provider>,
  );
}

describe('<ResourceMenu>', () => {
  it('renders resource menu correctly', () => {
    const wrapper = createResourceMenu();
    wrapper.find('.selector').simulate('click');

    expect(wrapper.find('.menu .search-wrapper')).toHaveLength(1);
    expect(wrapper.find('.menu > ul')).toHaveLength(2);
    expect(wrapper.find('.menu > ul').find(ResourceItem)).toHaveLength(3);
    expect(wrapper.find('.menu .static-links')).toHaveLength(1);
    expect(
      wrapper.find('.menu #resource-ResourceMenu--all-resources'),
    ).toHaveLength(1);
    expect(
      wrapper.find('.menu #resource-ResourceMenu--all-projects'),
    ).toHaveLength(1);
  });

  it('searches resource items correctly', () => {
    const SEARCH = 'bc';
    const wrapper = createResourceMenu();
    wrapper.find('.selector').simulate('click');

    act(() => {
      wrapper.find('.menu .search-wrapper input').prop('onChange')({
        currentTarget: { value: SEARCH },
      });
    });
    wrapper.update();

    expect(wrapper.find('.menu .search-wrapper input').prop('value')).toEqual(
      SEARCH,
    );
    expect(wrapper.find('.menu > ul').find(ResourceItem)).toHaveLength(2);
  });

  it('hides resource selector for all-projects', () => {
    const wrapper = createResourceMenu({ project: 'all-projects' });

    expect(wrapper.find('.resource-menu .selector')).toHaveLength(0);
  });

  it('renders resource selector correctly', () => {
    const wrapper = createResourceMenu();

    const selector = wrapper.find('.resource-menu .selector');
    expect(selector).toHaveLength(1);
    expect(selector.prop('title')).toEqual('path/to.file');
    expect(selector.find('span:first-child').text()).toEqual('to.file');
    expect(selector.find('.icon')).toHaveLength(1);
  });

  it('sets a localized resource name correctly for all-resources', () => {
    const wrapper = createResourceMenu({ resource: 'all-resources' });

    expect(wrapper.find('#resource-ResourceMenu--all-resources')).toHaveLength(
      1,
    );
  });

  it('renders resource menu correctly', () => {
    const wrapper = createResourceMenu();

    expect(wrapper.find('ResourceMenuDialog')).toHaveLength(0);
    wrapper.find('.selector').simulate('click');
    expect(wrapper.find('ResourceMenuDialog')).toHaveLength(1);
  });
});
