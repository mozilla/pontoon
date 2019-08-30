import React from 'react';
import { shallow } from 'enzyme';

import ProjectItem from './ProjectItem.js';

import { ProjectMenuBase } from './ProjectMenu';


function createShallowProjectMenu({
    project = 'project',
    resource = 'path/to.file',
} = {}) {
    return shallow(
        <ProjectMenuBase
            parameters={
                {
                    locale: 'locale',
                    project: project,
                    resource: resource,
                }
            }
            locale={
                {
                    code: 'locale',
                }
            }
            project={
                {
                    name: 'Project',
                    slug: 'project',
                }
            }
            resources={
                {
                    resources: [
                        {
                            path: 'resourceAbc',
                        },
                        {
                            path: 'resourceBcd',
                        },
                        {
                            path: 'resourceCde',
                        },
                    ],
                }
            }
        />
    );
}


describe('<ProjectMenu>', () => {
    it('shows a link to localization dashboard in regular view', () => {
        const wrapper = createShallowResourceMenu();

        expect(wrapper.text()).toContain('Project');
        expect(wrapper.find('a').prop('href')).toEqual('/locale/project/');
    });

    it('shows project selector in all projects view', () => {
        const wrapper = createShallowResourceMenu();

        expect(wrapper.find('.project-menu .selector')).toHaveLength(1);
        expect(wrapper.find('.project-menu .selector span:first-child').text()).toEqual('to.file');
        expect(wrapper.find('.project-menu .selector .icon')).toHaveLength(1);
    });

    it('renders project menu correctly', () => {
        const wrapper = createShallowResourceMenu();
        wrapper.instance().setState({visible: true});

        expect(wrapper.find('.project-menu .menu')).toHaveLength(1);
        expect(wrapper.find('.project-menu .menu .search-wrapper')).toHaveLength(1);
        expect(wrapper.find('.project-menu .menu > ul')).toHaveLength(2);
        expect(wrapper.find('.project-menu .menu > ul').find(ResourceItem)).toHaveLength(3);
    });

    it('searches project items correctly', () => {
        const SEARCH = 'bc';
        const wrapper = createShallowResourceMenu();
        wrapper.instance().setState({
            search: SEARCH,
            visible: true,
        });

        expect(wrapper.find('.project-menu .menu .search-wrapper input').prop('value')).toEqual(SEARCH);
        expect(wrapper.find('.project-menu .menu > ul').find(ResourceItem)).toHaveLength(2);
    });
});
