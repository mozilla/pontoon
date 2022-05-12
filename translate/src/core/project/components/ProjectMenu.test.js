import { shallow } from 'enzyme';
import React from 'react';
import sinon from 'sinon';

import { ProjectItem } from './ProjectItem';

import { ProjectMenu, ProjectMenuDialog } from './ProjectMenu';

beforeAll(() => sinon.stub(React, 'useContext'));
afterAll(() => React.useContext.restore());

function createShallowProjectMenuDialog({
  project = {
    slug: 'project',
    name: 'Project',
  },
} = {}) {
  React.useContext.returns({
    code: 'locale',
    localizations: [{ project }],
  });
  return shallow(<ProjectMenuDialog parameters={{ project: project.slug }} />);
}

describe('<ProjectMenu>', () => {
  it('renders properly', () => {
    const wrapper = createShallowProjectMenuDialog();

    expect(wrapper.find('.menu .search-wrapper')).toHaveLength(1);
    expect(wrapper.find('.menu > ul')).toHaveLength(1);
    expect(wrapper.find('.menu > ul').find(ProjectItem)).toHaveLength(1);
  });

  it('returns no results for non-matching searches', () => {
    const SEARCH_NO_MATCH = 'bc';
    const wrapper = createShallowProjectMenuDialog({
      project: ALL_PROJECTS,
    });

    wrapper
      .find('.menu .search-wrapper input')
      .simulate('change', { currentTarget: { value: SEARCH_NO_MATCH } });

    expect(wrapper.find('.menu .search-wrapper input').prop('value')).toEqual(
      SEARCH_NO_MATCH,
    );
    expect(wrapper.find('.menu > ul').find(ProjectItem)).toHaveLength(0);
  });

  it('searches project items correctly', () => {
    const SEARCH_MATCH = 'roj';
    const wrapper = createShallowProjectMenuDialog({
      project: ALL_PROJECTS,
    });

    wrapper
      .find('.menu .search-wrapper input')
      .simulate('change', { currentTarget: { value: SEARCH_MATCH } });

    expect(wrapper.find('.menu .search-wrapper input').prop('value')).toEqual(
      SEARCH_MATCH,
    );
    expect(wrapper.find('.menu > ul').find(ProjectItem)).toHaveLength(1);
  });
});

function createShallowProjectMenu({
  project = {
    slug: 'project',
    name: 'Project',
  },
} = {}) {
  React.useContext.returns({
    code: 'locale',
    localizations: [{ project }],
  });
  return shallow(
    <ProjectMenu
      parameters={{
        project: project.slug,
      }}
      project={{
        name: project.name,
        slug: project.slug,
      }}
    />,
  );
}

const ALL_PROJECTS = {
  slug: 'all-projects',
  name: 'All Projects',
};

describe('<ProjectMenuBase>', () => {
  it('shows a link to localization dashboard in regular view', () => {
    const wrapper = createShallowProjectMenu();

    expect(wrapper.text()).toContain('Project');
    expect(wrapper.find('a').prop('href')).toEqual('/locale/project/');
  });

  it('shows project selector in all projects view', () => {
    const wrapper = createShallowProjectMenu({ project: ALL_PROJECTS });

    expect(wrapper.find('.project-menu .selector')).toHaveLength(1);
    expect(wrapper.find('#project-ProjectMenu--all-projects')).toHaveLength(1);
    expect(wrapper.find('.project-menu .selector .icon')).toHaveLength(1);
  });

  it('renders the project menu upon clicking on all projects', () => {
    const wrapper = createShallowProjectMenu({ project: ALL_PROJECTS });
    wrapper.find('.selector').simulate('click');

    expect(wrapper.find('ProjectMenuDialog')).toHaveLength(1);
  });
});
