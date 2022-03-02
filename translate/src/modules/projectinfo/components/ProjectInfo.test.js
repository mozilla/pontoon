import React from 'react';
import { shallow } from 'enzyme';

import ProjectInfoBase, { ProjectInfo } from './ProjectInfo';

describe('<ProjectInfo>', () => {
    it('displays project info with HTML unchanged (', () => {
        const PREVALIDATED_HTML = '<a href="#">test</a>';
        const wrapper = shallow(
            <ProjectInfo project={{ info: PREVALIDATED_HTML }} />,
        );

        expect(wrapper.find('p').html()).toContain(PREVALIDATED_HTML);
    });
});

describe('<ProjectInfoBase>', () => {
    const PROJECT = {
        fetching: false,
        name: 'hello',
        info: 'Hello, World!',
    };

    it('shows only a button by default', () => {
        const wrapper = shallow(<ProjectInfoBase project={PROJECT} />);

        expect(wrapper.find('.button').exists()).toBeTruthy();
        expect(wrapper.find('ProjectInfo').exists()).toBeFalsy();
    });

    it('shows the info panel after a click', () => {
        const wrapper = shallow(<ProjectInfoBase project={PROJECT} />);
        wrapper.find('.button').simulate('click');

        expect(wrapper.find('ProjectInfo').exists()).toBeTruthy();
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
