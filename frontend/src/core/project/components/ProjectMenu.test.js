import React from 'react';
import { shallow } from 'enzyme';

import ProjectItem from './ProjectItem.js';

import { ProjectMenuBase } from './ProjectMenu';

function createShallowProjectMenu({
    project = {
        slug: 'project',
        name: 'Project',
    },
} = {}) {
    return shallow(
        <ProjectMenuBase
            parameters={{
                project: project.slug,
            }}
            locale={{
                code: 'locale',
                localizations: [
                    {
                        project: project,
                    },
                ],
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

describe('<ProjectMenu>', () => {
    it('shows a link to localization dashboard in regular view', () => {
        const wrapper = createShallowProjectMenu();

        expect(wrapper.text()).toContain('Project');
        expect(wrapper.find('a').prop('href')).toEqual('/locale/project/');
    });

    it('shows project selector in all projects view', () => {
        const wrapper = createShallowProjectMenu({ project: ALL_PROJECTS });

        expect(wrapper.find('.project-menu .selector')).toHaveLength(1);
        expect(wrapper.find('#project-ProjectMenu--all-projects')).toHaveLength(
            1,
        );
        expect(wrapper.find('.project-menu .selector .icon')).toHaveLength(1);
    });

    it('renders project menu correctly', () => {
        const wrapper = createShallowProjectMenu({ project: ALL_PROJECTS });
        wrapper.instance().setState({ visible: true });

        expect(wrapper.find('.project-menu .menu')).toHaveLength(1);
        expect(
            wrapper.find('.project-menu .menu .search-wrapper'),
        ).toHaveLength(1);
        expect(wrapper.find('.project-menu .menu > ul')).toHaveLength(1);
        expect(
            wrapper.find('.project-menu .menu > ul').find(ProjectItem),
        ).toHaveLength(1);
    });

    it('searches project items correctly', () => {
        const SEARCH_NO_MATCH = 'bc';
        const wrapper_no_match = createShallowProjectMenu({
            project: ALL_PROJECTS,
        });

        wrapper_no_match.instance().setState({
            search: SEARCH_NO_MATCH,
            visible: true,
        });

        expect(
            wrapper_no_match
                .find('.project-menu .menu .search-wrapper input')
                .prop('value'),
        ).toEqual(SEARCH_NO_MATCH);
        expect(
            wrapper_no_match.find('.project-menu .menu > ul').find(ProjectItem),
        ).toHaveLength(0);

        const SEARCH_MATCH = 'roj';
        const wrapper_match = createShallowProjectMenu({
            project: ALL_PROJECTS,
        });

        wrapper_match.instance().setState({
            search: SEARCH_MATCH,
            visible: true,
        });

        expect(
            wrapper_match
                .find('.project-menu .menu .search-wrapper input')
                .prop('value'),
        ).toEqual(SEARCH_MATCH);
        expect(
            wrapper_match.find('.project-menu .menu > ul').find(ProjectItem),
        ).toHaveLength(1);
    });
});
