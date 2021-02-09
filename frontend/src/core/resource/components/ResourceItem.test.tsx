import React from 'react';
import { shallow } from 'enzyme';

import ResourceItem from './ResourceItem';
import ResourcePercent from './ResourcePercent';

function createShallowResourceItem({ path = 'path' } = {}) {
    return shallow(
        <ResourceItem
            parameters={{
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
        const wrapper = createShallowResourceItem();
        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('a')).toHaveLength(1);
        expect(wrapper.find('span')).toHaveLength(1);
        expect(wrapper.find(ResourcePercent)).toHaveLength(1);
        expect(wrapper.find('a').prop('href')).toEqual('/locale/project/path/');
    });

    it('sets the className correctly', () => {
        let wrapper = createShallowResourceItem();
        expect(wrapper.find('li.current')).toHaveLength(0);

        wrapper = createShallowResourceItem({ path: 'resource' });
        expect(wrapper.find('li.current')).toHaveLength(1);
    });
});
