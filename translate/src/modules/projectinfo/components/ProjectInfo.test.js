import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { ProjectInfo } from './ProjectInfo';
import { fireEvent } from '@testing-library/react';

describe('<ProjectInfo>', () => {
  const PROJECT = { fetching: false, name: 'hello', info: 'Hello, World!' };

  it('shows only a button by default', () => {
    const store = createReduxStore({ project: PROJECT });
    const { container } = mountComponentWithStore(ProjectInfo, store);

    expect(container.querySelector('.button')).toBeInTheDocument();
    expect(container.querySelector('aside')).not.toBeInTheDocument();
  });

  it('shows the info panel after a click', () => {
    const store = createReduxStore({ project: PROJECT });
    const { container } = mountComponentWithStore(ProjectInfo, store);
    fireEvent.click(container.querySelector('.button'));

    expect(container.querySelector('aside.panel')).toBeInTheDocument();
  });

  it('returns null when data is being fetched', () => {
    const store = createReduxStore({ project: { ...PROJECT, fetching: true } });
    const wrapper = mountComponentWithStore(ProjectInfo, store);

    expect(wrapper.queryByTestId('project-info')).not.toBeInTheDocument();
  });

  it('returns null when info is null', () => {
    const store = createReduxStore({ project: { ...PROJECT, info: '' } });
    const wrapper = mountComponentWithStore(ProjectInfo, store);

    expect(wrapper.queryByTestId('project-info')).not.toBeInTheDocument();
  });

  it('displays project info with HTML unchanged (', () => {
    const html = '<a href="#">test</a>';
    const store = createReduxStore({ project: { ...PROJECT, info: html } });
    const { container } = mountComponentWithStore(ProjectInfo, store);
    fireEvent.click(container.querySelector('.button'));

    expect(container.querySelector('aside.panel')).toContainHTML(html);
  });
});
