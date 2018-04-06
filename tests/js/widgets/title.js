
import React from 'react';

import {shallow} from 'enzyme';

import {Title} from 'widgets/title';


test('Title render', () => {
    let title = shallow(
        <Title />);
    expect(title.text()).toBe('');
    expect(title.find('h1').length).toBe(0);

    title = shallow(
        <Title title="FOO" />);

    expect(title.text()).toBe('FOO');
    let h1 = title.find('h1');
    expect(h1.length).toBe(1);
    expect(h1.props().className).toBe(undefined);
    let anchor = h1.find('a');
    expect(anchor.props().href).toBe('#');
    expect(anchor.props().children).toEqual('FOO');

    title = shallow(
        <Title
           title="BAR"
           className="BAZ"
           href="/nowhere"
           />);
    h1 = title.find('h1');
    expect(h1.props().className).toBe('BAZ');
    anchor = h1.find('a');
    expect(anchor.props().href).toBe('/nowhere');
});
