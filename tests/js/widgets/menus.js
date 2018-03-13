
import React from 'react';

import {mount, shallow} from 'enzyme';

import {List, ListItem} from 'widgets/lists/generic';
import {Menu, MenuItem} from 'widgets/menus/generic';
import {DropdownMenu, DropdownMenuButton, DropdownMenuItem} from 'widgets/menus/dropdown';
import {ProfileDropdown} from 'widgets/menus';
import {ProfileMenu} from 'widgets/menus/profile/menu';
import {Avatar} from 'widgets/images';
import {Icon} from 'widgets/icons';
import {NotificationsDropdown} from 'widgets/menus';
import {NotificationsButton, NotificationsMenu,
        Notification} from 'widgets/menus/notifications';


test('Menu render', () => {
    let menu = shallow(<Menu items={[1, 2, 3]} />);
    expect(menu.text()).toBe('<List />');
    expect(menu.props()).toEqual(
        {className: "menu",
         components: {item: MenuItem},
         items: [{value: 1}, {value: 2}, {value: 3}]});

    menu = shallow(
        <Menu
           className="bar"
           components={{foo: 7, item: 23}}
           items={[4, 5, 6]} />);
    expect(menu.text()).toBe('<List />');
    expect(menu.props()).toEqual(
        {className: "bar",
         components: {item: 23, foo: 7},
         items: [{value: 4}, {value: 5}, {value: 6}]});
});


test('MenuItem render', () => {
    let item = shallow(<MenuItem />);
    expect(item.text()).toBe('<ListItem />');
    let listitem = item.find(ListItem);
    expect(listitem.props()).toEqual(
        {"children": undefined, "className": "menu-item"});

    item = shallow(<MenuItem className={23}>ITEM</MenuItem>);
    expect(item.text()).toBe('<ListItem />');
    listitem = item.find(ListItem);
    expect(listitem.props()).toEqual(
        {"children": "ITEM", "className": 23});
});


test('DropdownMenu render', () => {
    document.addEventListener = jest.fn();
    let menu = shallow(<DropdownMenu items={[1, 2, 3]} />);
    expect(menu.text()).toBe('<List />');
    const list = menu.find(List);
    expect(list.props().items).toEqual(
        [{"value": 1}, {"value": 2}, {"value": 3}]);
    expect(list.props().components).toEqual({"item": DropdownMenuItem});
    expect(list.props().className).toBe('menu dropdown');
    expect(document.addEventListener.mock.calls).toEqual(
        [["mousedown", menu.instance().handleClickOutside]]);
});


test('DropdownMenu componentWillUnmount', () => {
    document.removeEventListener = jest.fn();
    let menu = shallow(<DropdownMenu items={[1, 2, 3]} />);
    menu.instance().componentWillUnmount();
    expect(document.removeEventListener.mock.calls).toEqual(
        [["mousedown", menu.instance().handleClickOutside]]);
});


test('DropdownMenu handleClickOutside', () => {
    const handleClose = jest.fn();
    let menu = shallow(<DropdownMenu handleClose={handleClose} items={[1, 2, 3]} />);
    menu.instance().node = {contains: jest.fn(() => true)};
    menu.instance().handleClickOutside({target: 23});
    expect(handleClose.mock.calls).toEqual([]);

    menu.instance().node = {contains: jest.fn(() => false)};
    menu.instance().handleClickOutside({target: 23});
    expect(handleClose.mock.calls).toEqual([[{"target": 23}]]);
});


test('DropdownMenu components', () => {
    let menu = shallow(<DropdownMenu components={{item: 7, other: 23}} items={[1, 2, 3]} />);
    const list = menu.find(List);
    expect(list.props().components).toEqual({"item": 7, "other": 23});
});


test('DropdownMenu ref', () => {
    let menu = mount(<DropdownMenu items={[1, 2, 3]} />);
    const node = menu.find('div').first();
    expect(menu.instance().node).toBe(node.instance());
});


test('DropdownMenuItem render', () => {
    let item = shallow(<DropdownMenuItem />);
    expect(item.text()).toBe('<ListItem />');
    expect(item.props().className).toBe("menu-item horizontal-separator");

    item = shallow(<DropdownMenuItem>FOO</DropdownMenuItem>);
    expect(item.text()).toBe('<ListItem />');
    expect(item.props().className).toBe("menu-item");
    expect(item.props().children).toBe("FOO");
});


test('DropdownMenuButton render', () => {

    class MockButton extends React.PureComponent {
        render () {
            return 'BUTTON';
        }
    }

    const components = {button: MockButton};
    const button = shallow(
        <DropdownMenuButton
           foo={7}
           bar={23}
           components={components} />);
    expect(button.text()).toBe('<MockButton />');
    expect(button.state().open).toBe(false);
    const wrapper = button.find('div.button.selector');
    expect(wrapper.length).toBe(1);
    expect(wrapper.props().onClick).toBe(button.instance().handleClick);

    const buttonContent = wrapper.find(MockButton);
    expect(buttonContent.length).toBe(1);
    expect(buttonContent.props().foo).toBe(7);
    expect(buttonContent.props().bar).toBe(23);

});


test('DropdownMenuButton mount', () => {

    class MockButton extends React.PureComponent {
        render () {
            return 'BUTTON';
        }
    }

    class MockMenu extends React.PureComponent {
        render () {
            return 'MENU';
        }
    }

    const components = {
        button: MockButton,
        menu: MockMenu};
    const button = mount(
        <DropdownMenuButton
           foo={7}
           bar={23}
           components={components} />);
    expect(button.text()).toBe('BUTTON');
    button.setState({open: true});
    expect(button.text()).toBe('BUTTONMENU');

    const wrapper = button.find('div.button.selector');
    expect(button.instance().buttonNode).toBe(wrapper.instance());

    const menuContent = button.find(MockMenu);
    expect(menuContent.length).toBe(1);
    expect(menuContent.props().handleClose).toBe(button.instance().handleClose);
    expect(menuContent.props().foo).toBe(7);
    expect(menuContent.props().bar).toBe(23);
});



test('DropdownMenuButton handleClick', () => {

    class MockButton extends React.PureComponent {
        render () {
            return 'BUTTON';
        }
    }

    class MockMenu extends React.PureComponent {
        render () {
            return 'MENU';
        }
    }

    const components = {
        button: MockButton,
        menu: MockMenu};
    const button = shallow(
        <DropdownMenuButton
           foo={7}
           bar={23}
           components={components} />);
    expect(button.state().open).toBe(false);
    button.instance().handleClick();
    expect(button.state().open).toBe(true);
    button.instance().handleClick();
    expect(button.state().open).toBe(false);
});


test('DropdownMenuButton handleClose', () => {

    class MockButton extends React.PureComponent {
        render () {
            return 'BUTTON';
        }
    }

    class MockMenu extends React.PureComponent {
        render () {
            return 'MENU';
        }
    }

    const components = {
        button: MockButton,
        menu: MockMenu};
    const button = shallow(
        <DropdownMenuButton
           foo={7}
           bar={23}
           components={components} />);

    button.instance().handleClick();
    button.setState({open: true});
    const buttonNode = {contains: jest.fn(() => true)};
    button.instance().buttonNode = buttonNode;
    button.instance().handleClose({target: 7});
    expect(buttonNode.contains.mock.calls).toEqual([[7]]);
    expect(button.state().open).toBe(true);

    buttonNode.contains = jest.fn(() => false);
    button.instance().handleClose({target: 23});
    expect(buttonNode.contains.mock.calls).toEqual([[23]]);
    expect(button.state().open).toBe(false);
});


test('ProfileDropdown render', () => {
    let dropdown = shallow(<ProfileDropdown />);
    expect(dropdown.text()).toBe('');

    dropdown = shallow(<ProfileDropdown toolbar={{user: 7}} />);
    expect(dropdown.text()).toBe("<DropdownMenuButton />");
    let button = dropdown.find(DropdownMenuButton);
    expect(button.props()).toEqual(
        {buttonProps: {
            className: "rounded",
            name: 'navicon'},
         className: "select",
         components: {
             button: Icon,
             menu: ProfileMenu},
         id: "profile",
         menuProps: {
             menus: undefined,
             user: 7}});

    dropdown = shallow(
        <ProfileDropdown
           buttonProps={7}
           menuProps={13}
           components={{button: 23, menu: 43, baz: 17}}
           toolbar={{user: {avatar: 73}}} />);
    expect(dropdown.text()).toBe("<DropdownMenuButton />");
    button = dropdown.find(DropdownMenuButton);
    expect(button.props()).toEqual(
        {buttonProps: {
            className: "rounded",
            src: 73},
         className: "select",
         components: {
             button: Avatar,
             menu: ProfileMenu},
         id: "profile",
         menuProps: {
             menus: undefined,
             user: {avatar: 73}}});

});


test('ProfileMenu render', () => {

    class MockProfileMenu extends ProfileMenu {

        get items () {
            return ['AVATAR', 'SIGNOUT'];
        }
    }

    let menu = shallow(<MockProfileMenu />);
    expect(menu.text()).toBe('');

    menu = shallow(<MockProfileMenu foo={7} bar={23} user={{avatar: 23}} />);
    expect(menu.text()).toBe("<DropdownMenu />");

    const dropdown = menu.find(DropdownMenu);
    expect(dropdown.props()).toEqual({
        foo: 7,
        bar: 23,
        items: ["AVATAR", "SIGNOUT"],
        user: {"avatar": 23}});
});


test('ProfileMenu renderAvatar', () => {
    let menu = shallow(<ProfileMenu user={{avatar: 23, email: 17}} />);
    let avatar = shallow(menu.instance().renderAvatar());
    expect(avatar.text()).toBe("<ImageLink />");
    let {children, ...props} = avatar.props();
    expect(props).toEqual({
         className: "avatar",
         components: {image: Avatar},
         imageProps: {
             className: "rounded",
             height: undefined,
             width: undefined},
         src: 23});
    let name = shallow(children[0]);
    expect(name.text()).toBe('17');
    expect(name.props()).toEqual({children: 17, className: "name"});

    let email = shallow(children[1]);
    expect(email.text()).toBe('17');
    expect(email.props()).toEqual({children: 17, className: "email"});
});


test('ProfileMenu renderMenuItems', () => {
    const menu = shallow(<ProfileMenu />);
    const items = menu.instance().renderMenuItems([
        {href: 1, icon: 2, text: 3},
        {href: 4, icon: 5, text: 6}]);
    expect(items.length).toBe(2);
    const item0 = shallow(items[0]);
    expect(item0.props()).toEqual({"children": [<Icon name={2} />, 3], "href": 1});
    expect(item0.text()).toBe("<Icon />3");
    const item1 = shallow(items[1]);
    expect(item1.props()).toEqual({"children": [<Icon name={5} />, 6], "href": 4});
    expect(item1.text()).toBe("<Icon />6");
});


test('ProfileMenu items', () => {
    const renderMenuItems = jest.fn(() => [7, 23]);

    class MockProfileMenu extends ProfileMenu {

        get csrf () {
            return 'CRSFTOKEN';
        }

        renderMenuItems (item) {
            return renderMenuItems(item);
        }
    }

    let menu = shallow(<MockProfileMenu />);
    menu.instance().renderAvatar = jest.fn(() => 'AVATAR');

    let items = menu.instance().items;
    expect(items).toEqual([]);

    menu = shallow(
        <MockProfileMenu
           menus={{foo: 7, bar: 23, user: 17}}
           user={{username: 17}} />);
    menu.instance().renderAvatar = jest.fn(() => 'AVATAR');
    menu.instance().renderSignout = jest.fn(() => 'SIGNOUT');
    items = menu.instance().items;
    expect(items).toEqual(
        ["AVATAR", null, 7, 23, null, 7, 23, null, 7, 23, "SIGNOUT"]);
    // menus have been rendered twice
    expect(renderMenuItems.mock.calls).toEqual(
        [[7], [23], [17], [7], [23], [17]]);
});


test('ProfileMenu handleFormLoad', () => {
    let menu = shallow(<ProfileMenu />);
    menu.instance().handleFormLoad(23);
    expect(menu.instance().signoutForm).toBe(23);
});


test('ProfileMenu handleSignout', () => {
    let menu = shallow(<ProfileMenu />);
    menu.instance().signoutForm = {submit: jest.fn()};
    const evt = {preventDefault: jest.fn()};
    menu.instance().handleSignout(evt);

    expect(menu.instance().signoutForm.submit.mock.calls).toEqual([[]]);
    expect(evt.preventDefault.mock.calls).toEqual([[]]);
});


test('NotificationsDropdown render', () => {
    let dropdown = shallow(<NotificationsDropdown />);
    expect(dropdown.text()).toBe("<DropdownMenuButton />");

    let button = dropdown.find(DropdownMenuButton);
    expect(button.props()).toEqual(
        {className: "select",
         components: {
             button: NotificationsButton,
             menu: NotificationsMenu},
         id: "notification"});
});


test('NotificationsButton render', () => {
    const button = shallow(<NotificationsButton />);
    expect(button.text()).toBe("<Icon />");
    const icon = button.find(Icon);
    expect(icon.props()).toEqual({name: "bell-o"});
});


test('Notification render', () => {

    class MockNotification extends Notification {

        renderActor () {
            return 'ACTOR';
        }

        renderDescription () {
            return 'DESCRIPTION';
        }

        renderTarget () {
            return 'TITLE';
        }

        renderTime () {
            return 'TIME';
        }

        renderVerb () {
            return 'VERB';
        }
    }

    const notification = shallow(<MockNotification />);
    expect(notification.text()).toBe("ACTORVERBTITLETIMEDESCRIPTION");
});


test('Notification renderActor', () => {

    const notification = shallow(<Notification />);
    expect(notification.instance().renderActor()).toBe('');

    notification.setProps({actor: {url: 7, anchor: 'ANCHOR'}});
    expect(notification.instance().renderActor()).toEqual(
            <span className="actor"><a href={7}>ANCHOR</a></span>);

});


test('Notification renderDescription', () => {

    const notification = shallow(<Notification />);
    expect(notification.instance().renderDescription()).toEqual(
        <div className="message" />);

    notification.setProps({description: 'DESCRIPTION'});
    expect(notification.instance().renderDescription()).toEqual(
        <div className="message">DESCRIPTION</div>);
});


test('Notification renderTarget', () => {
    const notification = shallow(<Notification />);
    expect(notification.instance().renderTarget()).toBe('');

    notification.setProps({url: 'URL', target: 'TARGET'});
    expect(notification.instance().renderTarget()).toEqual(
        <span className="target"><a href="URL">TARGET</a></span>);
});


test('Notification renderTime', () => {
    const notification = shallow(<Notification />);
    expect(notification.instance().renderTime()).toBe('');

    notification.setProps({ago: 'AGO'});
    const time = shallow(notification.instance().renderTime());
    expect(time.props()).toEqual(
        {children: ["AGO", " ago"],
         className: "timeago"});
});


test('Notification renderVerb', () => {
    const notification = shallow(<Notification />);
    expect(notification.instance().renderVerb()).toEqual(
      <span className="verb" />);

    notification.setProps({verb: 'VERB'});
    expect(notification.instance().renderVerb()).toEqual(
        <span className="verb">VERB</span>);
});


test('NotificationsMenu render', () => {

    class MockNotificationsMenu extends NotificationsMenu {

        get items () {
            return [7, 23];
        }
    }

    const menu = shallow(<MockNotificationsMenu />);
    expect(menu.text()).toEqual("<DropdownMenu />");
    expect(menu.props()).toEqual({items: [7, 23]});
});


test('NotificationsMenu items', () => {
    const renderNotification = jest.fn(() => "NOTIFICATION");

    class MockNotificationsMenu extends NotificationsMenu {

        render () {
            return 'MENU';
        }

        renderNoNotifications () {
            return 'NO_NOTIFICATIONS';
        }

        renderNotification (notification) {
            return renderNotification(notification);
        }

        renderNotificationsLink () {
            return "LINK";
        }
    }

    let menu = shallow(
        <MockNotificationsMenu
           toolbar={{notifications: []}}
           />);
    expect(menu.instance().items).toEqual(
        ["NO_NOTIFICATIONS",
         null,
         "LINK"]);

    menu = shallow(
        <MockNotificationsMenu
           toolbar={{notifications: [1, 2, 3]}}
           />);
    expect(menu.instance().items).toEqual(
        ["NOTIFICATION", "NOTIFICATION", "NOTIFICATION",
         null, "LINK"]);
    expect(renderNotification.mock.calls).toEqual(
        [[1], [2], [3]]);
});


test('NotificationsMenu renderNotification', () => {

    class MockNotificationsMenu extends NotificationsMenu {

        render () {
            return 'MENU';
        }
    }

    let menu = shallow(<MockNotificationsMenu />);

    expect(menu.instance().renderNotification({foo: 7, bar: 23})).toEqual(
        <Notification bar={23} foo={7} />);
});


test('NotificationsMenu renderNotificationsLink', () => {

    class MockNotificationsMenu extends NotificationsMenu {

        render () {
            return 'MENU';
        }
    }

    let menu = shallow(<MockNotificationsMenu />);
    expect(menu.instance().renderNotificationsLink()).toEqual(
        <div className="see-all"><a href="/notifications/">See all Notifications</a></div>);
});


test('NotificationsMenu renderNoNotifications', () => {

    class MockNotificationsMenu extends NotificationsMenu {

        render () {
            return 'MENU';
        }
    }

    let menu = shallow(<MockNotificationsMenu />);
    expect(menu.instance().renderNoNotifications()).toEqual(
        <div className="no-notifications">
          <Icon name="bell" />
          <p className="title">No new notifications.</p>
          <p className="description">Here you’ll see updates for localizations you contribute to.</p>
        </div>);
});
