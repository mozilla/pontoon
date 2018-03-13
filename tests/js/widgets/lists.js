
import React from 'react';

import {shallow} from 'enzyme';

import {InfoList, InfoListItem} from 'widgets/lists/info';
import {List, ListItem} from 'widgets/lists/generic';
import {LinkList, LinkListItem} from 'widgets/lists/links';
import {Tab, TabCount, TabList} from 'widgets/lists/tabs';


test('List render', () => {
    let list = shallow(<List />);
    expect(list.text()).toBe('');

    // children are taken from either label or value
    // props are passed from this.props and the items attrs
    const items = [
        {value: 1, foo: 13, bar: 23},
        {label: 2},
        {label: 3}];
    list = shallow(
        <List
           bar={17}
           baz={113}
           items={items} />);
    expect(list.text()).toBe("<ListItem /><ListItem /><ListItem />");
    let listitem = list.find(ListItem).first();
    expect(listitem.props().children).toBe(1);
    expect(listitem.props().components).toEqual({});
    expect(listitem.props().foo).toBe(13);
    expect(listitem.props().bar).toBe(23);
    expect(listitem.props().baz).toBe(113);

    listitem = list.find(ListItem).last();
    expect(listitem.props().children).toBe(3);
    expect(listitem.props().components).toEqual({});
});


test('List render components', () => {
    let list = shallow(<List />);
    expect(list.text()).toBe('');
    const items = [
        {value: 1, foo: 13, bar: 23},
        {label: 2},
        {label: 3}];
    list = shallow(
        <List
           components={{comp1: 23, comp2: 43}}
           items={items} />);
    expect(list.text()).toBe("<ListItem /><ListItem /><ListItem />");
    let listitem = list.find(ListItem).first();
    expect(listitem.props().components).toEqual({"comp1": 23, "comp2": 43});
    listitem = list.find(ListItem).last();
    expect(listitem.props().components).toEqual({"comp1": 23, "comp2": 43});
});


test('ListItem render', () => {
    let item = shallow(
        <ListItem>
          <big>ITEM</big>
        </ListItem>);
    expect(item.props().children).toEqual(<big>ITEM</big>);
    expect(item.text()).toBe('ITEM');
    let li = item.find('li');
    expect(li.props().className).toBe(undefined);
    item = shallow(
        <ListItem className="FOO">
          <big>ITEM</big>
        </ListItem>);
    li = item.find('li');
    expect(li.props().className).toBe('FOO');
});


test('LinkListItem render', () => {
    const item = shallow(
        <LinkListItem
           href={23}>
          ITEM
        </LinkListItem>);
    expect(item.text()).toBe('<ListItem />');
    const listitem = item.find(ListItem);
    expect(listitem.props().className).toBe('link');
    expect(listitem.props().children).toEqual(<a href={23}>ITEM</a>);
});


test('LinkList render', () => {
    const linklist = shallow(
        <LinkList />);
    expect(linklist.text()).toBe('<List />');
    expect(linklist.instance().components.item).toBe(LinkListItem);
    const list = linklist.find(List);
    expect(list.props().className).toBe('links');
});


test('LinkList components', () => {
    const components = {item: 23};
    const list = shallow(
        <LinkList components={components} />);
    expect(list.instance().components.item).toBe(23);
});


test('LinkList items', () => {
    const links = [{href: 'FOO', label: 7}, {href: 'BAR', label: 23}];
    const linklist = shallow(<LinkList links={links} />);
    const list = linklist.find(List);
    expect(list.props().items).toEqual(links);
});


test('TabList render', () => {
    let tabs = shallow(<TabList />);
    expect(tabs.text()).toBe('');

    const tabdescriptors = [
        {label: 7, href: 'FOO', count: 43},
        {label: 13, active: true, href: 'BAR', count: 73},
        {label: 23, href: 'BAZ', count: 113}];
    tabs = shallow(<TabList tabs={tabdescriptors} />);
    expect(tabs.text()).toBe("<LinkList />");

    const list = tabs.find(LinkList);
    expect(list.length).toBe(1);
    expect(list.props().links).toBe(tabdescriptors);
    expect(list.props().components.item).toBe(Tab);
    expect(list.props().components.count).toBe(TabCount);
});


test('Tab render', () => {

    class MockCount extends React.Component {

        render () {
            return 'COUNT!';
        }
    }

    let tab = shallow(
        <Tab components={{count: MockCount}}
             href="FOO"
             count={23}>
          BAR
        </Tab>);
    expect(tab.text()).toBe("<LinkListItem />");
    let item = tab.find(LinkListItem);
    expect(item.length).toBe(1);
    expect(item.props().className).toBe('tab link');
    expect(item.props().href).toBe('FOO');
    expect(item.props().children).toEqual(
        ["BAR", <MockCount count={23} />]);

    tab = shallow(
        <Tab components={{count: MockCount}}
             href="FOO"
             label="BAR"
             active={true}
             count={23} />);
    item = tab.find(LinkListItem);
    expect(item.props().className).toBe('active tab link');
});


test('TabCount render', () => {
    let count = shallow(<TabCount />);
    expect(count.text()).toBe('');
    count = shallow(
        <TabCount count={23} />);
    expect(count.text()).toBe('23');
    let span = count.find('span');
    expect(span.length).toBe(1);
    expect(span.props().className).toBe('count');
    expect(span.props().children).toBe(23);
});



test('InfoList render', () => {
    let infolist = shallow(<InfoList />);
    expect(infolist.text()).toBe('');

    infolist = shallow(<InfoList items={{foo: 7, bar: 23}} />);
    expect(infolist.text()).toBe('<List />');

    let list = infolist.find(List);
    expect(list.props()).toEqual(
        {className: 'details',
         components: {item: InfoListItem},
         items: [['foo', 7], ['bar', 23]]});

    infolist = shallow(
        <InfoList
           className="something-else"
           components={{item: 13, baz: 17}}
           items={{foo: 7, bar: 23}} />);
    list = infolist.find(List);
    expect(list.props()).toEqual(
        {className: 'something-else',
         components: {
             baz: 17,
             item: 13},
         items: [['foo', 7], ['bar', 23]]});
});


test('InfoListItem render', () => {
    const props = ['foo bAr', 'baz'];
    let listitem = shallow(<InfoListItem {...props} />);
    expect(listitem.text()).toBe('<ListItem />');
    let item = listitem.find(ListItem);
    const children = [
            <span className="title">foo bAr</span>,
            <span className="value overflow">baz</span>];
    expect(item.props()).toEqual(
            {children: children,
             className: "foo-bar"});
});
