import React from 'react';
import { shallow } from 'enzyme';

import { ProjectItem } from './ProjectItem';

function createShallowProjectItem({ slug = 'slug' } = {}) {
  return shallow(
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
    const wrapper = createShallowProjectItem();
    expect(wrapper.find('li')).toHaveLength(1);
    expect(wrapper.find('a')).toHaveLength(1);
    expect(wrapper.find('span.project')).toHaveLength(1);
    expect(wrapper.find('span.percent')).toHaveLength(1);
    expect(wrapper.find('a').prop('href')).toEqual(
      '/locale/slug/all-resources/',
    );
  });

  it('sets the className for the current project', () => {
    const wrapper = createShallowProjectItem({ slug: 'project' });
    expect(wrapper.find('li.current')).toHaveLength(1);
  });

  it('sets the className for another project', () => {
    const wrapper = createShallowProjectItem();
    expect(wrapper.find('li.current')).toHaveLength(0);
  });

  it('renders completion percentage correctly', () => {
    const wrapper = createShallowProjectItem();
    expect(wrapper.find('.percent').text()).toEqual('50%');
  });
});
