import React from 'react';
import { shallow } from 'enzyme';

import ResourceItem from './ResourceItem.js';

import { ResourceMenuBase } from './ResourceMenu';

function createShallowResourceMenu({
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
        const wrapper = createShallowResourceMenu({ project: 'all-projects' });

        expect(wrapper.find('.resource-menu .selector')).toHaveLength(0);
    });

    it('renders resource selector correctly', () => {
        const wrapper = createShallowResourceMenu();

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
        const wrapper = createShallowResourceMenu({
            resource: 'all-resources',
        });

        expect(
            wrapper.find('#resource-ResourceMenu--all-resources'),
        ).toHaveLength(1);
    });

    it('renders resource menu correctly', () => {
        const wrapper = createShallowResourceMenu();
        wrapper.instance().setState({ visible: true });

        expect(wrapper.find('.resource-menu .menu')).toHaveLength(1);
        expect(
            wrapper.find('.resource-menu .menu .search-wrapper'),
        ).toHaveLength(1);
        expect(wrapper.find('.resource-menu .menu > ul')).toHaveLength(2);
        expect(
            wrapper.find('.resource-menu .menu > ul').find(ResourceItem),
        ).toHaveLength(3);
        expect(wrapper.find('.resource-menu .menu .static-links')).toHaveLength(
            1,
        );
        expect(
            wrapper.find(
                '.resource-menu .menu #resource-ResourceMenu--all-resources',
            ),
        ).toHaveLength(1);
        expect(
            wrapper.find(
                '.resource-menu .menu #resource-ResourceMenu--all-projects',
            ),
        ).toHaveLength(1);
    });

    it('searches resource items correctly', () => {
        const SEARCH = 'bc';
        const wrapper = createShallowResourceMenu();
        wrapper.instance().setState({
            search: SEARCH,
            visible: true,
        });

        expect(
            wrapper
                .find('.resource-menu .menu .search-wrapper input')
                .prop('value'),
        ).toEqual(SEARCH);
        expect(
            wrapper.find('.resource-menu .menu > ul').find(ResourceItem),
        ).toHaveLength(2);
    });
});
