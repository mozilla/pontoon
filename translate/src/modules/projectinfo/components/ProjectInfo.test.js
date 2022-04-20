import React from 'react';
import { shallow } from 'enzyme';

import { ProjectInfo } from './ProjectInfo';

describe('<ProjectInfo>', () => {
  const PROJECT = { fetching: false, name: 'hello', info: 'Hello, World!' };

  it('shows only a button by default', () => {
    const wrapper = shallow(<ProjectInfo project={PROJECT} />);

    expect(wrapper.find('.button').exists()).toBeTruthy();
    expect(wrapper.find('aside').exists()).toBeFalsy();
  });

  it('shows the info panel after a click', () => {
    const wrapper = shallow(<ProjectInfo project={PROJECT} />);
    wrapper.find('.button').simulate('click');

    expect(wrapper.find('ProjectInfoPanel').exists()).toBeTruthy();
  });

  it('returns null when data is being fetched', () => {
    const project = { ...PROJECT, fetching: true };
    const wrapper = shallow(<ProjectInfo project={project} />);

    expect(wrapper.type()).toBeNull();
  });

  it('returns null when info is null', () => {
    const project = { ...PROJECT, info: '' };
    const wrapper = shallow(<ProjectInfo project={project} />);

    expect(wrapper.type()).toBeNull();
  });

  it('displays project info with HTML unchanged (', () => {
    const PREVALIDATED_HTML = '<a href="#">test</a>';
    const wrapper = shallow(
      <ProjectInfo project={{ info: PREVALIDATED_HTML }} />,
    );
    wrapper.find('.button').simulate('click');

    expect(wrapper.find('ProjectInfoPanel').html()).toContain(
      PREVALIDATED_HTML,
    );
  });
});
