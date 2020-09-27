import React from 'react';
import { shallow } from 'enzyme';

import { ProjectInfoBase } from './ProjectInfo';

describe('<ProjectInfo>', () => {
    const PROJECT = {
        fetching: false,
        name: 'hello',
        info: 'Hello, World!',
    };

    it('shows only a button by default', () => {
        const wrapper = shallow(<ProjectInfoBase project={PROJECT} />);

        expect(wrapper.find('.button').exists()).toBeTruthy();
        expect(wrapper.find('.panel').exists()).toBeFalsy();
    });

    it('shows the info panel after a click', () => {
        const wrapper = shallow(<ProjectInfoBase project={PROJECT} />);
        wrapper.find('.button').simulate('click');

        expect(wrapper.find('.panel').exists()).toBeTruthy();
    });

    it('returns null when data is being fetched', () => {
        const project = {
            ...PROJECT,
            fetching: true,
        };
        const wrapper = shallow(<ProjectInfoBase project={project} />);

        expect(wrapper.type()).toBeNull();
    });

    it('returns null when info is null', () => {
        const project = {
            ...PROJECT,
            info: '',
        };
        const wrapper = shallow(<ProjectInfoBase project={project} />);

        expect(wrapper.type()).toBeNull();
    });

    it('returns null when project is all-projects', () => {
        const wrapper = shallow(
            <ProjectInfoBase projectSlug={'all-projects'} project={PROJECT} />,
        );

        expect(wrapper.type()).toBeNull();
    });
});
