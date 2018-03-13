
import React from 'react';

import {LinkList, LinkListItem} from './links';

import './tabs.css';


export class TabList extends React.PureComponent {

    get components () {
        const {item, count} = (this.props.components || {});
        return {
            item: item || Tab,
            count: count || TabCount};
    }

    render () {
        if (!this.props.tabs) {
            return '';
        }
        return (
            <LinkList
               links={this.props.tabs || []}
               className="tabs links"
               components={this.components}
               />);
    }
}


export class Tab extends React.PureComponent {

    render () {
        const TabCount = this.props.components.count;
        const className = this.props.active ? 'active tab link' : 'tab link';
        return (
            <LinkListItem
               className={className}
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
