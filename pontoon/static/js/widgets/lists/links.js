
import React from 'react';

import {getComponents} from 'utils/components';
import {List, ListItem} from './generic';

import './links.css';


export class LinkListItem extends React.PureComponent {
    className = 'link';

    render () {
        return (
            <ListItem className={this.props.className || this.className}>
              <a href={this.props.href} onClick={this.props.handleClick} name={this.props.name || ''}>
                {this.props.children}
              </a>
            </ListItem>);
    }
}


export class LinkList extends React.PureComponent {
    className = 'links';
    components = {item: LinkListItem};

    render () {
        const {components, className, links, ...props} = this.props;
        return (
            <List
               components={getComponents(this)}
               className={className || this.className}
               items={links}
               {...props} />);
    }
}
