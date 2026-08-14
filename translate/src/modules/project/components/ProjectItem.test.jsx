import React from 'react';

import { ProjectItem } from './ProjectItem';
import { render } from '@testing-library/react';

function renderProjectItem({ slug = 'slug' } = {}) {
  return render(
    <ProjectItem
      location={{
        locale: 'locale',
        project: 'project',
        resource: 'resource',
      }}
      localization={{
        project: { slug, name: 'Project' },
        approvedStrings: 2,
        stringsWithWarnings: 3,
        totalStrings: 10,
      }}
    />,
  );
}

describe('<ProjectItem>', () => {
  it('renders correctly', () => {
    const { getByRole, container } = renderProjectItem();
    getByRole('listitem');
    expect(container.querySelector('span.project')).toBeInTheDocument();
    expect(container.querySelector('span.percent')).toBeInTheDocument();
    expect(getByRole('link')).toHaveAttribute(
      'href',
      '/locale/slug/all-resources/',
    );
  });

  it('sets the className for the current project', () => {
    const { getByRole } = renderProjectItem({ slug: 'project' });
    expect(getByRole('listitem')).toHaveClass('current');
  });

  it('sets the className for another project', () => {
    const { getByRole } = renderProjectItem();
    expect(getByRole('listitem')).not.toHaveClass('current');
  });

  it('renders completion percentage correctly', () => {
    const { getByText } = renderProjectItem();
    getByText('50%');
  });
});
