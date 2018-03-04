
import React from 'react';

import {mount, shallow} from 'enzyme';

import {List, ListItem} from 'widgets/lists/generic';
import {Menu, MenuItem} from 'widgets/menus/generic';
import {DropdownMenu, DropdownMenuButton, DropdownMenuItem} from 'widgets/menus/dropdown';


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

    const components = {button: MockButton}
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
    button.setState({open: true})
    expect(button.text()).toBe('BUTTONMENU');

    const wrapper = button.find('div.button.selector');
    expect(button.instance().buttonNode).toBe(wrapper.instance());

    const menuContent = button.find(MockMenu);
    expect(menuContent.length).toBe(1)
    expect(menuContent.props().handleClose).toBe(button.instance().handleClose);
    expect(menuContent.props().foo).toBe(7)
    expect(menuContent.props().bar).toBe(23)
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
    expect(button.state().open).toBe(false)
    button.instance().handleClick()
    expect(button.state().open).toBe(true)
    button.instance().handleClick()
    expect(button.state().open).toBe(false)
})


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

    button.instance().handleClick()
    button.setState({open: true});
    const buttonNode = {contains: jest.fn(() => true)};
    button.instance().buttonNode = buttonNode;
    button.instance().handleClose({target: 7});
    expect(buttonNode.contains.mock.calls).toEqual([[7]])
    expect(button.state().open).toBe(true);

    buttonNode.contains = jest.fn(() => false);
    button.instance().handleClose({target: 23});
    expect(buttonNode.contains.mock.calls).toEqual([[23]])
    expect(button.state().open).toBe(false);
})
