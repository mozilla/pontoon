
import React from 'react';

import {shallow} from 'enzyme';

import {Icon} from 'widgets/icons';
import {SearchControls} from 'widgets/search';


test('SearchControls render', () => {
    const controls = shallow(
        <SearchControls
           placeholder="PLACEHOLDER" />);
    expect(controls.text()).toBe("<Icon />");

    const menu = controls.find('menu.controls');
    expect(menu.length).toBe(1);

    const wrapper = menu.find('.search-wrapper.small.clearfix');
    expect(wrapper.length).toBe(1);

    expect(wrapper.props().children.length).toBe(2);
    expect(wrapper.props().children[0]).toEqual(<Icon name="search" />);
    expect(wrapper.props().children[1]).toEqual(
        <input
           autoComplete="off"
           autoFocus="off"
           className="table-filter"
           onChange={controls.instance().handleFilterChange}
           placeholder="PLACEHOLDER"
           type="search" />);
});


test('SearchControls handleFilterChange', () => {

    let controls = shallow(<SearchControls />);
    expect(controls.instance().handleFilterChange({target: {value: 23}})).toBe(undefined);

    const handleFilterChange = jest.fn(() => 7);

    controls = shallow(<SearchControls handleFilterChange={handleFilterChange} />);
    expect(controls.instance().handleFilterChange({target: {value: 23}})).toBe(7);

    expect(handleFilterChange.mock.calls).toEqual([[23]]);
});
