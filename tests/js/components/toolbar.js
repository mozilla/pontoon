
import React from 'react';

import {shallow} from 'enzyme';

import Toolbar from 'components/toolbar';
import ToolbarMenu from 'components/toolbar/menu';
import {Logo} from 'widgets/images';
import {LinkList} from 'widgets/lists/links';
import {NotificationsDropdown, ProfileDropdown} from 'widgets/menus';
import {Menu} from 'widgets/menus/generic';


test('Toolbar render', () => {
    let toolbar = shallow(<Toolbar />);
    expect(toolbar.text()).toBe('');
    expect(toolbar.find('nav').length).toBe(0);

    toolbar = shallow(<Toolbar toolbar={{logo: {foo: 7, bar: 23}}} />);
    expect(toolbar.text()).toBe("<Logo /><LinkList /><ToolbarMenu />");
    let icon = toolbar.find(Logo);
    expect(icon.props()).toEqual({"bar": 23, "foo": 7});

    let links = toolbar.find(LinkList);
    expect(links.props()).toEqual({"logo": {"bar": 23, "foo": 7}});

    let menu = toolbar.find(ToolbarMenu);
    expect(menu.props()).toEqual({"toolbar": {"logo": {"bar": 23, "foo": 7}}});
});


test('ToolbarMenu render', () => {
    let toolbar = shallow(<ToolbarMenu />);
    expect(toolbar.text()).toBe("<Menu />");

    let menu = toolbar.find(Menu);
    expect(menu.props()).toEqual({
        className: "menus",
        items: [<ProfileDropdown />]});

    toolbar = shallow(<ToolbarMenu toolbar={{user: {username: 23}}} />);
    menu = toolbar.find(Menu);
    expect(menu.props()).toEqual({
        className: "menus",
        items: [<NotificationsDropdown toolbar={{"user": {"username": 23}}} />,
                <ProfileDropdown toolbar={{"user": {"username": 23}}} />]});
});
