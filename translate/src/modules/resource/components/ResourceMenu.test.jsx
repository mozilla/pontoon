import { createMemoryHistory } from 'history';
import React from 'react';
import { Provider } from 'react-redux';

import { LocationProvider } from '~/context/Location';

import { createReduxStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { ResourceMenu } from './ResourceMenu';
import { fireEvent, render } from '@testing-library/react';
import { expect } from 'vitest';

const resources = [
  { path: 'resourceAbc' },
  { path: 'resourceBcd' },
  { path: 'resourceCde' },
];

const allResourcesText = 'test-all-resource';
const allProjectsText = 'test-all-projects';
const resourceFile = 'to.file';

function createResourceMenu({
  project = 'project',
  resource = `path/${resourceFile}`,
} = {}) {
  const store = createReduxStore({
    resource: {
      allResources: {},
      resources,
    },
  });
  const history = createMemoryHistory({
    initialEntries: [`/locale/${project}/${resource}/`],
  });
  return render(
    <Provider store={store}>
      <LocationProvider history={history}>
        <MockLocalizationProvider
          resources={[
            `resource-ResourceMenu--all-resources = ${allResourcesText}`,
            `resource-ResourceMenu--all-projects = ${allProjectsText}`,
          ]}
        >
          <ResourceMenu />
        </MockLocalizationProvider>
      </LocationProvider>
    </Provider>,
  );
}

describe('<ResourceMenu>', () => {
  it('renders resource menu correctly', () => {
    const { getAllByRole, getByRole, container } = createResourceMenu();
    fireEvent.click(getByRole('button', { name: resourceFile }));

    expect(
      container.querySelector('.menu .search-wrapper'),
    ).toBeInTheDocument();
    expect(getAllByRole('list')).toHaveLength(2);
    for (const resource of resources) {
      getByRole('link', { name: new RegExp(resource.path) });
    }
    getByRole('link', { name: new RegExp(allResourcesText) });
    getByRole('link', { name: new RegExp(allProjectsText) });
  });

  it('searches resource items correctly', () => {
    const SEARCH = 'bc';
    const { getByRole, queryByRole } = createResourceMenu();
    fireEvent.click(getByRole('button', { name: resourceFile }));

    fireEvent.change(getByRole('searchbox'), {
      target: { value: SEARCH },
    });

    expect(getByRole('searchbox')).toHaveValue(SEARCH);
    getByRole('link', { name: new RegExp(resources[0].path) });
    getByRole('link', { name: new RegExp(resources[1].path) });
    expect(
      queryByRole('link', { name: new RegExp(resources[2].path) }),
    ).toBeNull();
  });

  it('hides resource selector for all-projects', () => {
    const { queryByRole } = createResourceMenu({ project: 'all-projects' });

    expect(queryByRole('button')).toBeNull();
  });

  it('renders resource selector correctly', () => {
    const { getByRole } = createResourceMenu();

    const selector = getByRole('button', { name: resourceFile });
    expect(selector).toHaveAttribute('title', 'path/to.file');
    expect(selector.querySelector('span:first-child')).toHaveTextContent(
      'to.file',
    );
    expect(selector.querySelector('.icon')).toBeInTheDocument();
  });

  it('sets a localized resource name correctly for all-resources', () => {
    const { getByText } = createResourceMenu({ resource: 'all-resources' });

    getByText(allResourcesText);
  });

  it('renders resource menu correctly', () => {
    const { container, getByRole } = createResourceMenu();

    expect(container.querySelector('.menu')).toBeNull();
    fireEvent.click(getByRole('button', { name: resourceFile }));
    expect(container.querySelector('.menu')).toBeInTheDocument();
  });
});
