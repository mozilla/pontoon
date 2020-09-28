import React from 'react';
import { shallow } from 'enzyme';

import { ResourceProgressBase } from './ResourceProgress';

describe('<ResourceProgress>', () => {
    const STATS = {
        approved: 5,
        fuzzy: 4,
        unreviewed: 5,
        warnings: 3,
        errors: 2,
        missing: 1,
        total: 15,
    };
    const PARAMETERS = {
        entity: 0,
        locale: 'en-GB',
        project: 'tutorial',
        resource: 'all-resources',
        status: 'errors',
        search: null,
    };

    it('shows only a selector by default', () => {
        const wrapper = shallow(
            <ResourceProgressBase stats={STATS} parameters={PARAMETERS} />,
        );

        expect(wrapper.find('.selector').exists()).toBeTruthy();
        expect(wrapper.find('.menu').exists()).toBeFalsy();
    });

    it('shows the info menu after a click', () => {
        const wrapper = shallow(
            <ResourceProgressBase stats={STATS} parameters={PARAMETERS} />,
        );
        wrapper.find('.selector').simulate('click');

        expect(wrapper.find('.menu').exists()).toBeTruthy();
    });
});
