import React from 'react';

import { ResourceItem } from './ResourceItem';
import { render } from '@testing-library/react';
import { expect } from 'vitest';

function renderResourceItem({ path = 'path', ...otherResourceProps } = {}) {
  return render(
    <ResourceItem
      location={{
        locale: 'locale',
        project: 'project',
        resource: 'resource',
      }}
      resource={{
        path: path,
        ...otherResourceProps,
      }}
    />,
  );
}

describe('<ResourceItem>', () => {
  it('renders correctly', () => {
    const path = 'test-path';
    const { getByRole, getByText } = renderResourceItem({
      path,
      approvedStrings: 2,
      stringsWithWarnings: 2,
      totalStrings: 10,
    });
    getByRole('listitem');
    expect(getByRole('link')).toHaveAttribute(
      'href',
      `/locale/project/${path}/`,
    );
    expect(getByText(path)).toHaveClass('path');
    expect(getByText('40%')).toHaveClass('percent');
  });

  it('sets the className correctly', () => {
    let { container } = renderResourceItem();
    expect(container.querySelector('li.current')).toBeNull();

    container = renderResourceItem({ path: 'resource' }).container;
    expect(container.querySelector('li.current')).toBeInTheDocument();
  });
});
