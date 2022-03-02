import React from 'react';
import { shallow } from 'enzyme';

import { NavigationBase } from './Navigation';

describe('<Navigation>', () => {
    const LOCALE = {
        code: 'kg',
        name: 'Klingon',
    };
    const PROJECT = {
        name: 'Mark 42',
    };
    const PARAMETERS = {
        locale: 'kg',
        project: 'mark42',
        resource: 'stuff.ftl',
    };

    it('shows navigation', () => {
        const wrapper = shallow(
            <NavigationBase
                locale={LOCALE}
                parameters={PARAMETERS}
                project={PROJECT}
            />,
        );

        expect(wrapper.text()).toContain('Klingon');
        expect(wrapper.text()).toContain('kg');
    });
});
