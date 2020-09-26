import React from 'react';
import { shallow } from 'enzyme';

import ProjectItem from './ProjectItem';
import ProjectPercent from './ProjectPercent';

function createShallowProjectItem({ slug = 'slug' } = {}) {
    return shallow(
        <ProjectItem
            parameters={{
                locale: 'locale',
                project: 'project',
                resource: 'resource',
            }}
            localization={{
                project: {
                    slug: slug,
                    name: 'Project',
                },
            }}
        />,
    );
}

describe('<ProjectItem>', () => {
    it('renders correctly', () => {
        const wrapper = createShallowProjectItem();
        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('a')).toHaveLength(1);
        expect(wrapper.find('span')).toHaveLength(1);
        expect(wrapper.find(ProjectPercent)).toHaveLength(1);
        expect(wrapper.find('a').prop('href')).toEqual(
            '/locale/slug/all-resources/',
        );
    });

    it('sets the className correctly', () => {
        let wrapper = createShallowProjectItem();
        expect(wrapper.find('li.current')).toHaveLength(0);

        wrapper = createShallowProjectItem({ slug: 'project' });
        expect(wrapper.find('li.current')).toHaveLength(1);
    });
});
