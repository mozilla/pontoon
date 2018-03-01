
import React from 'react';

import {getComponent, getComponents} from 'utils/components';
import {LinkList, LinkListItem} from './links';

import './tabs.css';


export class TabList extends React.PureComponent {
    components = {
        item: Tab,
        count: TabCount};

    render () {
        const {tabs, components, ...props} = this.props;
        return (
            <LinkList
               links={tabs || []}
               className="tabs links"
               components={getComponents(this)}
               {...props}
               />);
    }
}


export class Tab extends React.PureComponent {

    render () {
        const TabCount = getComponent(this, 'count');
        return (
            <LinkListItem
               className={this.props.active ? 'active tab link' : 'tab link'}
               href={this.props.href}>
              {this.props.children}
              <TabCount count={this.props.count} />
            </LinkListItem>);
    }
}


export class TabCount extends React.PureComponent {

    render () {
        if (this.props.count) {
            return <span className="count">{this.props.count}</span>;
        }
        return '';
    }
}
