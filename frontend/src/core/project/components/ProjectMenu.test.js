import React from 'react';
import { shallow } from 'enzyme';

import { ProjectMenuBase } from './ProjectMenu';


describe('<ProjectMenu>', () => {
    const LOCALE = {
        code: 'kg',
    };
    const PARAMETERS = {
        locale: 'kg',
        project: 'mark42',
        resource: 'stuff.ftl',
    };
    const PROJECT = {
        name: 'Mark 42',
        slug: 'mark42',
    };

    it('shows a link to localization dashboard in regular view', () => {
        const wrapper = shallow(<ProjectMenuBase
            locale={ LOCALE }
            parameters={ PARAMETERS }
            project={ PROJECT }
        />);

        expect(wrapper.text()).toContain('Mark 42');
        expect(wrapper.find('a').prop('href')).toEqual('/kg/mark42/');
    });

    it('shows a link to locale dashboard in all projects vew', () => {
        const wrapper = shallow(<ProjectMenuBase
            locale={ LOCALE }
            parameters={ { ...PARAMETERS, project: 'all-projects' } }
            project={ PROJECT }
        />);

        expect(wrapper.text()).toContain('All Projects');
        expect(wrapper.find('a').prop('href')).toEqual('/kg/');
    });
});
