
import React from 'react';

import {shallow} from 'enzyme';

import {Icon, IconLink} from 'widgets/icons';


test('Icon render', () => {
    let icon = shallow(<Icon />);
    expect(icon.text()).toBe('');
    let i = icon.find('i');
    expect(i.length).toBe(0);
    icon = shallow(<Icon name="foo" />);
    expect(icon.text()).toBe('');
    i = icon.find('i');
    expect(i.length).toBe(1);
    expect(i.props().className).toBe("icon fa fa-foo fa-fw");
    icon = shallow(<Icon name="foo" className="something else" />);
    expect(icon.text()).toBe('');
    i = icon.find('i');
    expect(i.length).toBe(1);
    expect(i.props().className).toBe("icon fa fa-foo fa-fw something else");
});


test('IconLink render', () => {
    let iconlink = shallow(<IconLink />);
    expect(iconlink.text()).toBe('');
    iconlink = shallow(
        <IconLink
           icon='bar'
           href='/nowhere'
           baz={23}>
          ICONTEXT
        </IconLink>);
    expect(iconlink.text()).toBe('<Icon />ICONTEXT');
    const anchor = iconlink.find('a');
    expect(anchor.props()).toEqual(
        {"baz": 23,
         "children": [<Icon name="bar" />,
                      "ICONTEXT"],
         "href": "/nowhere"});
});
