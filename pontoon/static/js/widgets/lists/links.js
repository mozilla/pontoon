
import React from 'react';

import {List, ListItem} from './generic';

import './links.css';


export class LinkListItem extends React.PureComponent {

    get className () {
        return this.props.className || 'link';
    }

    render () {
        return (
            <ListItem className={this.className}>
              <a href={this.props.href}>
                {this.props.children}
              </a>
            </ListItem>);
    }
}


export class LinkList extends React.PureComponent {

    get components () {
        const components = {item: LinkListItem};
        return Object.assign({}, components, (this.props.components || {}));
    }

    get className () {
        return this.props.className || 'links';
    }

    render () {
        return (
            <List
               components={this.components}
               className={this.className}
               items={this.props.links} />);
    }
}
