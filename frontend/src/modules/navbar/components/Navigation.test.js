import React from 'react';
import { shallow } from 'enzyme';

import { NavigationBase } from './Navigation';


describe('<Navigation>', () => {
    const LOCALE = {
        code: 'kg',
        name: 'Klingon'
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
        const wrapper = shallow(<NavigationBase
            locale={ LOCALE }
            parameters={ PARAMETERS }
            project={ PROJECT }
        />);

        expect(wrapper.text()).toContain('Klingon');
        expect(wrapper.text()).toContain('kg');
        expect(wrapper.text()).toContain('Mark 42');
    });

    it('shows a link to locale dashboard when all projects are loaded', () => {
        const wrapper = shallow(<NavigationBase
            locale={ LOCALE }
            parameters={ { ...PARAMETERS, project: 'all-projects' } }
            project={ PROJECT }
        />);

        expect(wrapper.text()).toContain('All Projects');

        const links = wrapper.find('a');
        // Link 1 is locale dashboard, we want to make sure project link (2)
        // goes there too.
        expect(links.at(1).prop('href')).toEqual(links.at(2).prop('href'));
    });
});
