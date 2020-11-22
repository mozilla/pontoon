import React from 'react';

import { mount, shallow } from 'enzyme';

import Checkbox from 'widgets/checkbox';

test('Checkbox render', () => {
    let checkbox = shallow(<Checkbox />);
    expect(checkbox.text()).toBe('');
    expect(checkbox.instance().el.indeterminate).toBe(false);

    checkbox = shallow(<Checkbox indeterminate='true' />);
    expect(checkbox.text()).toBe('');
    expect(checkbox.instance().el.indeterminate).toBe(true);
    expect(checkbox.instance().el.nodeName).toBe(undefined);

    checkbox = mount(<Checkbox />);
    // this time el is an HTML node
    expect(checkbox.instance().el.indeterminate).toBe(false);
    expect(checkbox.instance().el.nodeName).toEqual('INPUT');

    checkbox = mount(<Checkbox indeterminate={true} />);
    expect(checkbox.instance().el.indeterminate).toBe(true);
    expect(checkbox.instance().el.nodeName).toEqual('INPUT');

    let prevProp = checkbox.props();
    checkbox.setProps({ indeterminate: false });
    checkbox.instance().componentDidUpdate(prevProp);
    expect(checkbox.instance().el.indeterminate).toBe(false);
    expect(checkbox.instance().el.nodeName).toEqual('INPUT');

    prevProp = checkbox.props();
    checkbox.setProps({ indeterminate: true });
    checkbox.instance().componentDidUpdate(prevProp);
    expect(checkbox.instance().el.indeterminate).toBe(true);
    expect(checkbox.instance().el.nodeName).toEqual('INPUT');
});
