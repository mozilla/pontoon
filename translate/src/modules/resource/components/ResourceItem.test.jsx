import React from 'react';

import { ResourceItem } from './ResourceItem';
import { render } from '@testing-library/react';

function renderResourceItem({ path = 'path' } = {}) {
  return render(
    <ResourceItem
      location={{
        locale: 'locale',
        project: 'project',
        resource: 'resource',
      }}
      resource={{
        path: path,
      }}
    />,
  );
}

describe('<ResourceItem>', () => {
  it('renders correctly', () => {
    const { getByRole, container } = renderResourceItem();
    getByRole('listitem');
    expect(getByRole('link')).toHaveAttribute('href', '/locale/project/path/');
    expect(container.querySelector('span.path')).toBeInTheDocument();
    expect(container.querySelector('span.percent')).toBeInTheDocument();
  });

  it('sets the className correctly', () => {
    let { container } = renderResourceItem();
    expect(container.querySelector('li.current')).toBeNull();

    container = renderResourceItem({ path: 'resource' }).container;
    expect(container.querySelector('li.current')).toBeInTheDocument();
  });
});
