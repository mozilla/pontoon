
import React from 'react';

import './info-list.css';

import {getComponents} from 'utils/components';
import {List, ListItem} from 'widgets/lists/generic';


export class InfoList extends React.PureComponent {
    className = "details"
    components = {item: InfoListItem};

    render () {
        if (!this.props.items) {
            return '';
        }
        return (
            <List
               className={this.props.className || this.className}
               items={Object.entries(this.props.items)}
               components={getComponents(this)} />);
    }
}


export class InfoListItem extends React.PureComponent {

    get className () {
        return this.props.className || this.props[0].toLowerCase().replace(' ', '-');
    }

    render () {
        const k = this.props[0];
        const v = this.props[1];
        return (
            <ListItem className={this.className}>
              <span className="title">{k}</span>
              <span className="value overflow">{v}</span>
            </ListItem>);
    }
}
