
import React from 'react';

import {shallow} from 'enzyme';

import {Icon} from 'widgets/icons';
import {Stars, Star} from 'widgets/stars';


test('Stars render', () => {
    let stars = shallow(<Stars />);
    expect(stars.text()).toBe('');
    stars = shallow(
        <Stars stars={3} />);
    expect(stars.text()).toBe("<Star /><Star /><Star />");
    stars = shallow(
        <Stars stars={5} />);
    expect(stars.text()).toBe("<Star /><Star /><Star /><Star /><Star />");
});


test('Star render', () => {
    let star = shallow(<Star />);
    expect(star.text()).toBe("<Icon />");
    let icon = star.find(Icon);
    expect(icon.length).toBe(1);
    expect(icon.props()).toEqual(
        {className: "star", name: "star"});
})
