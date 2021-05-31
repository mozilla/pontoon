import React from 'react';
import { shallow } from 'enzyme';

import ResourceItem from './ResourceItem';

import ResourceMenuBase, { ResourceMenu } from './ResourceMenu';

function createShallowResourceMenu({
    project = 'project',
    resource = 'path/to.file',
} = {}) {
    return shallow(
        <ResourceMenu
            parameters={{
                locale: 'locale',
                project: project,
                resource: resource,
            }}
            resources={{
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
            }}
        />,
    );
}

describe('<ResourceMenu>', () => {
    it('renders resource menu correctly', () => {
        const wrapper = createShallowResourceMenu();

        expect(wrapper.find('.menu .search-wrapper')).toHaveLength(1);
        expect(wrapper.find('.menu > ul')).toHaveLength(2);
        expect(wrapper.find('.menu > ul').find(ResourceItem)).toHaveLength(3);
        expect(wrapper.find('.menu .static-links')).toHaveLength(1);
        expect(
            wrapper.find('.menu #resource-ResourceMenu--all-resources'),
        ).toHaveLength(1);
        expect(
            wrapper.find('.menu #resource-ResourceMenu--all-projects'),
        ).toHaveLength(1);
    });

    it('searches resource items correctly', () => {
        const SEARCH = 'bc';
        const wrapper = createShallowResourceMenu();
        wrapper
            .find('.menu .search-wrapper input')
            .simulate('change', { currentTarget: { value: SEARCH } });

        expect(
            wrapper.find('.menu .search-wrapper input').prop('value'),
        ).toEqual(SEARCH);
        expect(wrapper.find('.menu > ul').find(ResourceItem)).toHaveLength(2);
    });
});

function createShallowResourceMenuBase({
    project = 'project',
    resource = 'path/to.file',
} = {}) {
    return shallow(
        <ResourceMenuBase
            parameters={{
                locale: 'locale',
                project: project,
                resource: resource,
            }}
            resources={{
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
            }}
        />,
    );
}

describe('<ResourceMenuBase>', () => {
    it('hides resource selector for all-projects', () => {
        const wrapper = createShallowResourceMenuBase({
            project: 'all-projects',
        });

        expect(wrapper.find('.resource-menu .selector')).toHaveLength(0);
    });

    it('renders resource selector correctly', () => {
        const wrapper = createShallowResourceMenuBase();

        expect(wrapper.find('.resource-menu .selector')).toHaveLength(1);
        expect(wrapper.find('.resource-menu .selector').prop('title')).toEqual(
            'path/to.file',
        );
        expect(
            wrapper.find('.resource-menu .selector span:first-child').text(),
        ).toEqual('to.file');
        expect(wrapper.find('.resource-menu .selector .icon')).toHaveLength(1);
    });

    it('sets a localized resource name correctly for all-resources', () => {
        const wrapper = createShallowResourceMenuBase({
            resource: 'all-resources',
        });

        expect(
            wrapper.find('#resource-ResourceMenu--all-resources'),
        ).toHaveLength(1);
    });

    it('renders resource menu correctly', () => {
        const wrapper = createShallowResourceMenuBase();

        expect(wrapper.find('ResourceMenu')).toHaveLength(0);
        wrapper.find('.selector').simulate('click');
        expect(wrapper.find('ResourceMenu')).toHaveLength(1);
    });
});
