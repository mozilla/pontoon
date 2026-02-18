import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { ProjectInfo } from './ProjectInfo';
import { fireEvent } from '@testing-library/react';

describe('<ProjectInfo>', () => {
  const PROJECT = { fetching: false, name: 'hello', info: 'Hello, World!' };

  it('shows only a button by default', () => {
    const store = createReduxStore({ project: PROJECT });
    const { getByRole, queryByRole } = mountComponentWithStore(
      ProjectInfo,
      store,
    );

    expect(getByRole('button')).toBeInTheDocument();
    expect(queryByRole('complementary')).not.toBeInTheDocument();
  });

  it('shows the info panel after a click', () => {
    const store = createReduxStore({ project: PROJECT });
    const { getByRole } = mountComponentWithStore(ProjectInfo, store);
    fireEvent.click(getByRole('button'));

    expect(getByRole('complementary')).toBeInTheDocument();
  });

  it('returns null when data is being fetched', () => {
    const store = createReduxStore({ project: { ...PROJECT, fetching: true } });
    const { container } = mountComponentWithStore(ProjectInfo, store);
    expect(container).toBeEmptyDOMElement();
  });

  it('returns null when info is null', () => {
    const store = createReduxStore({ project: { ...PROJECT, info: '' } });
    const { container } = mountComponentWithStore(ProjectInfo, store);

    expect(container).toBeEmptyDOMElement();
  });

  it('displays project info with HTML unchanged (', () => {
    const html = '<a href="#">test</a>';
    const store = createReduxStore({ project: { ...PROJECT, info: html } });
    const { getByRole } = mountComponentWithStore(ProjectInfo, store);
    fireEvent.click(getByRole('button'));

    expect(getByRole('complementary')).toContainHTML(html);
  });
});
