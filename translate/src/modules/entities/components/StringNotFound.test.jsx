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
  filters: [],
};

const FTL = `
entities-StringNotFound--title = String not found
entities-StringNotFound--description = doesn’t match
entities-StringNotFound--go-to-string = Show the string
entities-StringNotFound--show-matching = Keep the parameters
entities-StringNotFound--request-details = Request details
entities-StringNotFound--string-details = String { $stringId } details
entities-StringNotFound--label-locale = Locale
entities-StringNotFound--label-project = Project
entities-StringNotFound--label-resource = Resource
entities-StringNotFound--label-filters = Filters
entities-StringNotFound--label-string = String
entities-StringNotFound--all-projects = All Projects
entities-StringNotFound--all-resources = All Resources
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
  it('lays out where the requested string lives', () => {
    const { getByText } = mount(ENTITY_LOCATION);

    getByText('foo.ftl');
    getByText('99');
    getByText('Thunderbird');
  });

  it('lists the mismatched filters when the string is hidden by filters', () => {
    const { getByText } = mount(
      {
        pk: 99,
        project: 'firefox',
        project_name: 'Firefox',
        resource: 'foo.ftl',
        filters: ['missing'],
      },
      '/kg/firefox/all-resources/?status=missing,warnings&string=99',
    );

    getByText('missing');
  });

  it('lists the active filters, splitting packed params into a clean list', () => {
    const { getByText } = mount(
      ENTITY_LOCATION,
      '/kg/firefox/all-resources/?status=missing,warnings&extra=fuzzy&string=99',
    );

    getByText('missing, warnings, and fuzzy');
  });

  it('labels the all-projects, all-resources view', () => {
    const { getByText } = mount(
      ENTITY_LOCATION,
      '/kg/all-projects/all-resources/?status=missing&string=99',
    );

    getByText('All Projects');
    getByText('All Resources');
  });

  it('primary action shows the string, dropping filters', () => {
    const { getByRole, spy } = mount(ENTITY_LOCATION);

    fireEvent.click(getByRole('link', { name: 'Show the string' }));

    const { pathname, search } = spy.mock.calls.at(-1)[0];
    expect(pathname).toBe('/kg/thunderbird/foo.ftl/');
    expect(search).toBe('?string=99');
  });

  it('secondary action keeps the parameters, dropping the string', () => {
    const { getByRole, spy } = mount(ENTITY_LOCATION);

    fireEvent.click(getByRole('link', { name: 'Keep the parameters' }));

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
