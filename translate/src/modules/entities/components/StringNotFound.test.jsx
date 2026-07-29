import { createMemoryHistory } from 'history';
import { fireEvent } from '@testing-library/react';
import { expect, vi } from 'vitest';

import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { StringNotFound } from './StringNotFound';

const ENTITY_LOCATION = {
  pk: 99,
  project: 'thunderbird',
  project_name: 'Thunderbird',
  resource: 'foo.ftl',
};

const FTL = `
entities-StringNotFound--description-filtered = filtered
entities-StringNotFound--description-in-project = in project
entities-StringNotFound--description-in-resource = in resource
entities-StringNotFound--description-in-all-projects = in all projects
entities-StringNotFound--go-to-string = go to string
entities-StringNotFound--show-matching = show matching
`;

function mount(
  entityLocation,
  url = '/kg/firefox/all-resources/?status=missing&string=99',
) {
  const history = createMemoryHistory({ initialEntries: [url] });
  const spy = vi.fn();
  history.listen(spy);
  const store = createReduxStore();
  const result = mountComponentWithStore(
    StringNotFound,
    store,
    { entityLocation },
    history,
    FTL,
  );
  return { ...result, spy };
}

describe('<StringNotFound>', () => {
  it('blames the filters when the string is in the open project and scope', () => {
    const { getByText } = mount({
      pk: 99,
      project: 'firefox',
      resource: 'toolbar.ftl',
    });

    getByText('filtered');
  });

  it('points to the project when the string lives in another project', () => {
    const { getByText } = mount(
      ENTITY_LOCATION,
      '/kg/firefox/all-resources/?string=99',
    );

    getByText('in project');
  });

  it('points to the resource when the string is elsewhere in the open project', () => {
    const { getByText } = mount(
      {
        pk: 99,
        project: 'firefox',
        project_name: 'Firefox',
        resource: 'foo.ftl',
      },
      '/kg/firefox/browser.ftl/?string=99',
    );

    getByText('in resource');
  });

  it('mentions all projects when viewing every project', () => {
    const { getByText } = mount(
      ENTITY_LOCATION,
      '/kg/all-projects/all-resources/?string=99',
    );

    getByText('in all projects');
  });

  it('goes to the string, dropping filters but keeping the string', () => {
    const { getByRole, spy } = mount(ENTITY_LOCATION);

    fireEvent.click(getByRole('button', { name: 'go to string' }));

    const { pathname, search } = spy.mock.calls.at(-1)[0];
    expect(pathname).toBe('/kg/thunderbird/foo.ftl/');
    expect(search).toBe('?string=99');
  });

  it('keeps the filters but drops the string', () => {
    const { getByRole, spy } = mount(ENTITY_LOCATION);

    fireEvent.click(getByRole('button', { name: 'show matching' }));

    const { pathname, search } = spy.mock.calls.at(-1)[0];
    expect(pathname).toBe('/kg/firefox/all-resources/');
    expect(search).toContain('status=missing');
    expect(search).not.toContain('string=');
  });

  it('renders nothing without a string location', () => {
    const { container } = mount(null);
    expect(container).toBeEmptyDOMElement();
  });
});
