
import React from 'react';

import {shallow} from 'enzyme';

import {Section} from 'widgets/section';


test('Section render', () => {
    let section = shallow(<Section />);
    expect(section.text()).toBe('');

    let node = section.find('section');
    expect(node.props()).toEqual(
        {children: <div className="wrapper" />,
         id: undefined});

    section = shallow(<Section id="foo" className="bar">SECTION</Section>);
    expect(section.text()).toBe('SECTION');
    node = section.find('section');
    expect(node.props()).toEqual(
        {children: <div className="bar">SECTION</div>,
         id: "foo"});
});
