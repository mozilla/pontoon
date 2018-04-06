
import React from 'react';

import {getComponents} from 'utils/components';
import {LinkList, LinkListItem} from './links';

import './buttons.css';


export class Buttons extends React.PureComponent {
    components = {item: Button}

    get className () {
        const className = "buttons links"
        return this.props.className ? className + ' ' + this.props.className : className;
    }

    render () {
        const {buttons, components, ...props} = this.props;
        return (
            <LinkList
               links={buttons || []}
               {...props}
               className={this.className}
               components={getComponents(this)}
               />);
    }
}


export class Button extends React.PureComponent {

    render () {
        return (
            <LinkListItem
               handleClick={this.props.handleClick}
               className={this.props.active ? 'active button link' : 'button link'}
               name={this.props.name}
               href={this.props.href}>
              {this.props.children}
            </LinkListItem>);
    }
}
